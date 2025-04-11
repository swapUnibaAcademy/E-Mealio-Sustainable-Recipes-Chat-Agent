import service.bot.LangChainService as lcs
import Constants as p
import service.domain.FoodHistoryService as history
import service.domain.UserDataService as user
import service.SuggestRecipeService as food
import service.ImproveRecipeService as imp
import service.domain.IngredientService as ingService
import service.asyncr.ComputeMonthlyUserTasteService as taste
import dto.Response as rc
import jsonpickle
import service.ExpertRecipeService as er
import Utils as utils
import service.domain.FoodHistoryService as fhService
import service.bot.LogService as log
import datetime
import traceback

PRINT_LOG = True

def answer_router(userData,userPrompt,token,memory,info):
    response = rc.Response('','','','','')
    while(response.answer==''):
        try:
            response = answer_question(userData,userPrompt,token,memory,info)
        except Exception as e:
            error = "An error occurred: " + str(e)
            log.save_log(error, datetime.datetime.now(), "System", userData.id, PRINT_LOG)
            stacktarce = "Stacktrace: " + str(traceback.format_exc())
            log.save_log(stacktarce, datetime.datetime.now(), "System", userData.id, PRINT_LOG)
            response = rc.Response("I'm sorry, I was not able to process your request. Please send an email to a.iacovazzi6@studenti.uniba.it", "TOKEN 1", '', None, '')
            raise e
        token = response.action
        info = response.info
        memory = response.memory
        if(response.modifiedPrompt != None and response.modifiedPrompt != ''):
            userPrompt = response.modifiedPrompt
    manage_last_interaction(userData)
    return response   

def answer_question(userData,userPrompt,token,memory,info):
#0 USER DATA RETRIEVAL##################################################################
    if(token == p.TASK_0_HOOK):
        log.save_log("PRESENTING_USER_DATA_RETRIEVAL", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0, userPrompt, 0.6, userData)
        return response
    elif(token == p.TASK_0_1_HOOK):
        log.save_log("PERFORMING_USER_DATA_RETRIEVAL", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_1, "User data: " + userData.to_json() + " "+ userPrompt, 0.2, userData)
        return response
    elif(token == p.TASK_0_2_HOOK):
        log.save_log("PERFORMING_USER_DATA_EVALUATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #update user data using the information so far retrieved
        userData.from_json(info)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_2, "User data: " + userData.to_json(), 0.2, userData)
        return response
    elif(token == p.TASK_0_3_HOOK):
        log.save_log("PERSISTING_USER_DATA", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #persist user data calling MongoDB...
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_3, "User data: " + userData.to_json(), 0.4, userData)
        userData.reminder = False
        userData.tastes = taste.return_empty_tastes()
        user.save_user(userData)
        return response
    elif(token == p.TASK_0_4_HOOK):
         log.save_log("ASKING_PERMISSION_FOR_REMINDER", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
         response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_4, userPrompt, 0.4, userData)
         return response
    elif(token == p.TASK_0_5_HOOK):
        log.save_log("REMINDER_ACCEPTED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        userData.reminder = True 
        user.update_user(userData)
        response = rc.Response("I'm happy you accepted to receive reminders from me! If you forget to chat with me in two days, I will send you a message to help you stay on track with your sustainable habits!","TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        #adjust the user prompt to the greetings in order to start the regular conversation
        userPrompt = p.USER_GREETINGS_PHRASE
        return response
    elif(token == p.TASK_0_6_HOOK):
        log.save_log("REMINDER_DECLINED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = rc.Response("Ok, you decided not to receive reminders from me! If you change your mind, you can enable them by asking me to update your profile.","TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        #adjust the user prompt to the greetings in order to start the regular conversation
        userPrompt = p.USER_GREETINGS_PHRASE
        return response
########################################################################################
#-1 MEMORY CLEANING#####################################################################
    elif(token == p.TASK_MINUS_1_HOOK):
        log.save_log("MEMORY_CLEANING", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        memory = None
        fhService.clean_temporary_declined_suggestions(userData.id)
        return rc.Response('',"TOKEN 1",'',None,'')
#1 MAIN HUB / GREETINGS#################################################################
    elif(token == p.TASK_1_HOOK):
        log.save_log("GRETINGS", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #passing though the main hub imply starting a new conversation so I can reset the memory
        memory = None
        response = lcs.execute_chain(p.STARTING_PROMPT, userPrompt, 0.3, userData)
        return response
########################################################################################

#FOOD SUGGESTION########################################################################
    elif(token == p.TASK_2_HOOK):
        log.save_log("FOOD_SUGGESTION_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_2_PROMPT, userPrompt + ' ' + info, 0.1, userData)
        return response
    elif(token == p.TASK_2_05_HOOK):
        log.save_log("FOOD_SUGGESTION_DATA_VERIFICATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        json_mealdata_obj = jsonpickle.decode(info)

        #Meal type check and answer not managed by LLMS since it is straightforward
        if(json_mealdata_obj['mealType'] == None or json_mealdata_obj['mealType'] == ''):
            answer = """I need to know when you would like to eat the meal you desire.\nPlease provide a meal type between: breakfast, lunch, dinner or snack."""
            action = p.TASK_2_HOOK           
            response = rc.Response(answer,action,info,None,'')
        else:
            action = p.TASK_2_10_HOOK
            response = rc.Response('',action,info,None,'')
        return response
    elif(token == p.TASK_2_10_HOOK):
        log.save_log("PROVIDING_FOOD_SUGGESTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #call recommender system
        suggestedRecipe = utils.adapt_output_to_bot(food.get_recipe_suggestion(info,userData))
        info = utils.escape_curly_braces(info)
        userDataStr = utils.escape_curly_braces(userData.to_json())
        userPrompt = "Suggest me a recipe given the following constraints " + info
        if(suggestedRecipe != 'null'):
            response = lcs.execute_chain(p.TASK_2_10_PROMPT.format(suggestedRecipe=suggestedRecipe, mealInfo=info, userData=userDataStr), userPrompt, 0.6, userData, memory, True)
        else:
            response = lcs.execute_chain(p.TASK_2_10_1_PROMPT.format(mealInfo=info, userData=userDataStr), userPrompt, 0.6, userData, memory, False)        
        #produce suggestion
        return response
    elif(token == p.TASK_2_20_HOOK):
        log.save_log("SUGGESTION_CHAT_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_2_20_PROMPT, userPrompt, 0.6, userData, memory, True)
        return response
    elif(token == p.TASK_2_30_HOOK):
        log.save_log("SUGGESTION_ACCEPTED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"accepted")
        fhService.clean_temporary_declined_suggestions(userData.id)
        response = rc.Response('I\'m glad you accepted my suggestion! If I can help you with other food sustainability questions, I\'m here to help!',"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        return response
    elif(token == p.TASK_2_40_HOOK):
        log.save_log("SUGGESTION_DECLINED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"declined")
        fhService.clean_temporary_declined_suggestions(userData.id)
        response = rc.Response("That's okay! I hope you find something that suits you next time. If you have any other questions about food sustainability, I'm here to help!","TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        return response
    elif(token == p.TASK_2_50_HOOK):
        log.save_log("REQUIRED_ANOTHER_SUGGESTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"temporary_declined")
        originalUserPrompt = memory.messages[1].content
        response = rc.Response('',"TOKEN 1",'',None,originalUserPrompt)
        return response
########################################################################################

#RECIPE SUSTAINABILITY EXPERT###########################################################
    elif(token == p.TASK_3_HOOK):
        log.save_log("EXPERT_HUB", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_PROMPT, userPrompt, 0.1, userData)
        return response
########################################################################################

#RECIPE IMPROVEMENT#####################################################################
    elif(token == p.TASK_3_10_HOOK):
        log.save_log("RECIPE_IMPROVEMENT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_10_PROMPT, userPrompt+' '+info, 0.1, userData)
        return response
    elif(token == p.TASK_3_15_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_INGREDIENT_LIST_EVALUATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_15_PROMPT, userPrompt, 0.1, userData)
        #recover the previous info because the prompt do not generate new info
        response.info = info
        return response
    elif(token == p.TASK_3_20_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_EXECUTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #call the recipe improvement service
        baseRecipe = imp.get_base_recipe(info)
        improvedRecipe = utils.adapt_output_to_bot(imp.get_recipe_improved(baseRecipe,userData))
        if(improvedRecipe != 'null'):
            response = lcs.execute_chain(p.TASK_3_20_PROMPT.format(baseRecipe=utils.adapt_output_to_bot(baseRecipe), improvedRecipe=improvedRecipe), userPrompt, 0.1, userData, memory, True)
        else:
            None
            userDataStr = utils.escape_curly_braces(userData.to_json())
            response = lcs.execute_chain(p.TASK_3_20_1_PROMPT.format(baseRecipe=utils.adapt_output_to_bot(baseRecipe), userData=userDataStr), userPrompt, 0.1, userData)
        return response
    elif(token == p.TASK_3_30_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_CHAT_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_30_PROMPT, userPrompt, 0.6, userData, memory, True)
        return response
    elif(token == p.TASK_3_40_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_ACCEPTED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #save the improved recipe as consumed by the user since she will have to eat it
        manage_suggestion(userData,memory,"accepted",1)
        fhService.clean_temporary_declined_suggestions(userData.id)
        response = rc.Response('I\'m glad you accepted my improved version of the recipe! If I can help you with other food sustainability questions, I\'m here to help!',"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        return response
    elif(token == p.TASK_3_50_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_DECLINED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #don't save the rejected recipe, this because this don't have to be considered as a suggestion? i'm thinking about it
        manage_suggestion(userData,memory,"declined")
        fhService.clean_temporary_declined_suggestions(userData.id)
        response = rc.Response("That's okay! I hope you find something that suits you next time. If you have any other questions about food sustainability, I'm here to help!","TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        return response
    elif(token == p.TASK_3_60_HOOK):
        log.save_log("REQUIRED_ANOTHER_RECIPE_IMPROVEMENT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"temporary_declined",1)
        originalUserPrompt = memory.messages[1].content
        response = rc.Response('',"TOKEN 3.10",'',None,originalUserPrompt)
        return response
########################################################################################

#PROFILE MANAGEMENT#####################################################################
    elif(token == p.TASK_4_HOOK):
        log.save_log("PROFILE_SUMMARY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        userPrompt = p.USER_PROMPT.format(user_data=userData.to_json())
        response = lcs.execute_chain(p.TASK_4_PROMPT, userPrompt, 0.8, userData)
        return response
    elif(token == p.TASK_4_10_HOOK):
        log.save_log("ASKING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_4_10_PROMPT, userPrompt, 0.1, userData)
        return response
    elif(token == p.TASK_4_20_HOOK):
        log.save_log("PRESENTING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_4_20_PROMPT, userPrompt, 0.1, userData)
        return response
    elif(token == p.TASK_4_30_HOOK):
        log.save_log("PERFORMING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_4_30_PROMPT, "User data: "+ userPrompt, 0.1, userData)
        return response
    elif(token == p.TASK_4_40_HOOK):
        log.save_log("EVALUATING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        userData.update_from_json(info)
        response = lcs.execute_chain(p.TASK_4_40_PROMPT, "User data: " + userData.to_json() + " "+ userPrompt, 0.1, userData)
        return response
    elif(token == p.TASK_4_50_HOOK):
        log.save_log("PERSISTING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #persist user data calling MongoDB...
        response = lcs.execute_chain(p.TASK_4_50_PROMPT, "User data: " + userData.to_json(), 0.1, userData)
        user.update_user(userData)
        return response
########################################################################################

#HISTORY RETRIEVAL######################################################################
    elif(token == p.TASK_5_HOOK):
        log.save_log("FOOD_HISTORY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        foodHistory = utils.adapt_output_to_bot(history.get_user_history_of_week(userData.id))
        response = lcs.execute_chain(p.TASK_5_PROMPT.format(food_history=foodHistory), userPrompt, 0.3, userData, memory, True)
        return response
    elif(token == p.TASK_5_10_HOOK):
        log.save_log("FOOD_HISTORY_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_5_10_PROMPT, userPrompt, 0.3, userData, memory, True)
        if response.action == p.TASK_MINUS_1_HOOK:
            response.modifiedPrompt = p.USER_GREETINGS_PHRASE
        return response
########################################################################################

#SUSTAINABILITY EXPERT##################################################################
    elif(token == p.TASK_6_HOOK):
        log.save_log("SUSTAINABILITY_EXPERT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_6_PROMPT, userPrompt, 0.2, userData)
        return response
    elif(token == p.TASK_6_10_HOOK):
        log.save_log("SUSTAINABILITY_CONCEPT_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        conceptData = jsonpickle.decode(info)
        concept = conceptData['concept']
        response = lcs.execute_chain(p.TASK_6_10_PROMPT.format(concept = concept), userPrompt, 0.3, userData, memory, True)
        return response
    elif(token == p.TASK_6_20_HOOK):
        log.save_log("SUSTAINABILITY_INGREDIENTS_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        ingredientsData = jsonpickle.decode(info)
        ingredientsData = utils.adapt_output_to_bot(ingService.get_ingredient_list_from_generic_list_of_string(ingredientsData['ingredients']))
        response = lcs.execute_chain(p.TASK_6_20_PROMPT.format(ingredients = ingredientsData), userPrompt, 0.3, userData, memory, True)
        return response
    elif(token == p.TASK_6_30_HOOK):
        log.save_log("SUSTAINABILITY_RECIPE_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        recipesData = jsonpickle.decode(info)
        recipes = utils.adapt_output_to_bot(er.extractRecipes(recipesData))
        response = lcs.execute_chain(p.TASK_6_30_PROMPT.format(recipes = recipes), userPrompt, 0.3, userData, memory, True)
        return response
    elif(token == p.TASK_6_40_HOOK):
        log.save_log("SUSTAINABILITY_EXPERT_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_6_40_PROMPT, userPrompt, 0.3, userData, memory, True)
        if response.action == p.TASK_MINUS_1_HOOK:
            response.modifiedPrompt = p.USER_GREETINGS_PHRASE
        return response
########################################################################################

#RECIPE CONSUPTION DIARY################################################################
    elif(token == p.TASK_7_HOOK):
        log.save_log("RECIPE_CONSUPTION_DIARY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_7_PROMPT, "Meal data: " + info +" "+userPrompt, 0.2, userData)
        return response
    elif(token == p.TASK_7_10_HOOK):
        log.save_log("RECIPE_CONSUPTION_DIARY_DATA_VERIFICATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_7_10_PROMPT, "Meal data: " + info, 0.3, userData)
        return response
    elif(token == p.TASK_7_20_HOOK):
        log.save_log("RECIPE_CONSUPTION_DIARY_DATA_SAVING", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #calling the proper service to save the meal data computing the sustainability
        jsonRecipeAssertion = utils.extract_json(info, 0)
        fhService.build_and_save_user_history_from_user_assertion(userData, jsonRecipeAssertion)
        response = lcs.execute_chain(p.TASK_7_20_PROMPT, "Meal data: " + info, 0.1, userData)
        return response
########################################################################################

def manage_suggestion(userData,memory,status,whichJson=0):
    originalPrompt = utils.de_escape_curly_braces(memory.messages[0].content)
    jsonRecipe = utils.extract_json(originalPrompt, whichJson)
    fhService.build_and_save_user_history(userData, jsonRecipe, status)

def manage_last_interaction(userData):
    userData.lastInteraction = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user.update_user_last_interaction(userData.id, userData.lastInteraction)