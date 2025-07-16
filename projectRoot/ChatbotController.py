import service.bot.LangChainService as lcs
import service.bot.LogService as log
import service.bot.WebSearch as ws
import Constants as p
import Utils as utils
import dto.Response as rc
import service.domain.FoodHistoryService as history
import service.domain.UserDataService as user
import service.domain.IngredientService as ingService
import service.domain.FoodHistoryService as fhService
import service.domain.RecipeService as rcpService
import service.SuggestRecipeService as food
import service.ImproveRecipeService as imp
import service.ExpertRecipeService as er
import service.asyncr.ComputeMonthlyUserTasteService as taste
import jsonpickle
import datetime
import traceback

PRINT_LOG = True
"""Flag che indica se stampare i log (di default True)."""

def answer_router(userData,userPrompt,token,memory,info):
    """
    Args : 
    - userData : dati dell'utente che sta interagendo con il chatbot.
    - userPrompt : messaggio che l'utente ha inviato al chatbot.
    - token : token rappresentante lo stato corrente.
    - memory : eventuale memoria della conversazione con i messaggi scambiati precedentemente.
    - info : eventuali informazioni aggiuntive.

    Returns : 
    - response : 
    """

    print("\n####################################################################################################\nDebug (ChatBotController -> answer_router)")
             
    response = rc.Response('','','','','')

    """
    Se la risposta generata dal LLM contiene solo un token e non un messagio di testo, continuiamo a richiamare
    answer_question per effettuare le transizioni di stato corrispondenti ai token, fino ad ottenere una risposta
    di testo da inviare all'utente tramite il chatbot.
    """

    while(response.answer==''):  
        try:
            print("\nanswer_router ---- > answer_question\n")
            response = answer_question(userData,userPrompt,token,memory,info)

        except Exception as e:
            error = "An error occurred: " + str(e)
            log.save_log(error, datetime.datetime.now(), "System", userData.id, PRINT_LOG)
            stacktarce = "Stacktrace: " + str(traceback.format_exc())
            log.save_log(stacktarce, datetime.datetime.now(), "System", userData.id, PRINT_LOG)
            response = rc.Response("I'm sorry, I was not able to process your request. Please send an email to a.iacovazzi6@studenti.uniba.it", "TOKEN 1", '', None, '')
            raise e
        
        print("\n#### ",token, " ---->>> ",response.action, " ####")
        token = response.action
        info = response.info
        memory = response.memory
        if(response.modifiedPrompt != None and response.modifiedPrompt != ''):
            userPrompt = response.modifiedPrompt

    manage_last_interaction(userData)

    print("\n####################################################################################################\n")

    return response   

def answer_question(userData,userPrompt,token,memory,info):
    """
    Args : 
    - userData : dati dell'utente che sta interagendo con il chatbot.
    - userPrompt : messaggio che l'utente ha inviato al chatbot.
    - token : token che corrisponde allo stato in cui si trova il sistema (determinato da TASK_N_HOOK)
    - memory : eventuale memoria dei precedenti messaggi, per fornire contesto.
    - info : 

    Returns : 
    - response : risposta generata dal LLM (contiene il token dello stato in cui il sistema transita e 
    il testo del messaggio da fornire come risposta all'utente)
    
    """

    print("\n----------------------------------------------------------------------------------------------------\nDebug (ChatBotController -> answer_question)")
    print("\nuserData : \n", userData)
    print("\nuserPrompt : \n", userPrompt)
    print("\ntoken : \n", token)
    print("\nmemory : \n",memory)
    print("\ninfo : \n",info)
    
    """
    A seconda dello stato che il sistema si trova (determinato da TASK_N_HOOK), effettuiamo una chiamata al LLM
    passando in input il prompt corrispondente al TASK_N_HOOK (TASK_N_NN_PROMPT), il messaggio ricevuto dall'utente,
    la temperatura della specifica chimata al LLM ed i dati dell'utente.
    """

    # recuperiamo la lingua con cui l'utente vuole interagire con il chatbot
    # se per qualche motivo non è presente, si interagisce di default in inglese
    language = userData.language if userData.language is not None else "english"

#####################################################################################
# 0 USER DATA RETRIEVAL

    if(token == p.TASK_0_0_HOOK):
        log.save_log("PRESENTING_USER_LANGUAGE_RETRIEVAL", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        # print(f"##### {userData.username} : {userData.language}")
        response = lcs.execute_chain(p.GET_LANGUAGE_PROMPT_BASE_0_0.format(language_code=userData.language), userPrompt, 0.3, userData)
        return response
    
    if(token == p.TASK_0_0_1_HOOK):
        log.save_log("ASKING_USER_LANGUAGE_RETRIEVAL", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.GET_LANGUAGE_PROMPT_BASE_0_1.format(language_code=userData.language), userPrompt, 0.3, userData)
        return response
    
    if(token == p.TASK_0_0_2_HOOK):
        log.save_log("PERFORMING_USER_LANGUAGE_RETRIEVAL", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        userData.language = user.get_language_from_json(info)
        user.update_user(userData)

        # possiamo andare direttamente alla presentazione dei dati che l'utente deve inserire per registrarsi
        action = p.TASK_0_HOOK
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0.format(language=userData.language), userPrompt, 0.3, userData, memory, True) # qui usiamo userData.language e non userData.language perchè a questo punto arriviamo direttamente senza transizione tramite LLM
        return response
    
    if(token == p.TASK_0_HOOK):
        log.save_log("PRESENTING_USER_DATA_RETRIEVAL", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0.format(language=language), userPrompt, 0.6, userData)
        return response
    
    elif(token == p.TASK_0_1_HOOK):
        log.save_log("PERFORMING_USER_DATA_RETRIEVAL", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_1.format(language=language), "User data: " + userData.to_json() + " "+ userPrompt, 0.2, userData)
        return response
    
    elif(token == p.TASK_0_2_HOOK):
        log.save_log("PERFORMING_USER_DATA_EVALUATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)

        # l'utente ha inserito i dati nella sua lingua, ma affinche siano compatibili con il db li dobbiamo prima tradurre in inglese
        translated_info = lcs.translate_info(info, language, "allergies, restrictions, disliked_ingredients, evolving_diet")
        userData.from_json(translated_info)

        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_2.format(language=language), "User data: " + userData.to_json(), 0.2, userData)
        return response
    
    elif(token == p.TASK_0_3_HOOK):
        log.save_log("PERSISTING_USER_DATA", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #persist user data calling MongoDB...
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_3.format(language=language), "User data: " + userData.to_json(), 0.4, userData)
        userData.reminder = False
        userData.tastes = taste.return_empty_tastes()
        user.save_user(userData)
        return response
    
    elif(token == p.TASK_0_4_HOOK):
        log.save_log("ASKING_PERMISSION_FOR_REMINDER", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.GET_DATA_PROMPT_BASE_0_4.format(language=language), userPrompt, 0.4, userData)
        return response
    
    elif(token == p.TASK_0_45_HOOK):
        log.save_log("REMINDER_SETTING", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        # estraiamo le informazioni sul reminder custom dal json info
        days_reminder, hour_reminder = user.get_reminder_info(info)
        
        userData.reminder = True 
        userData.days_reminder = days_reminder
        userData.hour_reminder = hour_reminder
        user.update_user(userData)

        # not managed by LLMS since it is straightforward
        answer = lcs.translate_text(p.CUSTOM_REMINDER_ACCEPTED.format(days_reminder=days_reminder), language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)

        return response
    
    elif(token == p.TASK_0_5_HOOK):
        log.save_log("REMINDER_DEFAULT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
    
        userData.reminder = True 
        userData.days_reminder = 2
        userData.hour_reminder = 12
        user.update_user(userData)

        # not managed by LLMS since it is straightforward
        answer = lcs.translate_text(p.DEFAULT_REMINDER_ACCEPTED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        
        return response

    elif(token == p.TASK_0_6_HOOK):
        log.save_log("REMINDER_DECLINED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        answer = lcs.translate_text(p.REMINDER_DECLINED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        #adjust the user prompt to the greetings in order to start the regular conversation
        userPrompt = p.USER_GREETINGS_PHRASE
        return response
    
########################################################################################
# -1 MEMORY CLEANING

    elif(token == p.TASK_MINUS_1_HOOK):
        log.save_log("MEMORY_CLEANING", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        memory = None
        fhService.clean_temporary_declined_suggestions(userData.id)
        return rc.Response('',"TOKEN 1",'',None,'')
    
# 1 MAIN HUB / GREETINGS

    elif(token == p.TASK_1_HOOK):
        log.save_log("GRETINGS", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #passing though the main hub imply starting a new conversation so I can reset the memory
        memory = None
        response = lcs.execute_chain(p.STARTING_PROMPT.format(language =language), userPrompt, 0.3, userData)
        return response
    
########################################################################################
# 1.X PRE TASK 

    elif(token == p.TASK_PRE_2_HOOK):
        log.save_log("PRE_FOOD_SUGGESTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.PRE_TASK_2_PROMPT.format(language=language), userPrompt, 0.3, userData)
        return response
    
    elif(token == p.TASK_PRE_3_HOOK):
        log.save_log("PRE_RECIPE_IMPROVEMENT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.PRE_TASK_3_PROMPT.format(language=language), userPrompt, 0.3, userData)
        return response
    
    elif(token == p.TASK_PRE_4_HOOK):
        log.save_log("PRE_PROFILE_SUMMARY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.PRE_TASK_4_PROMPT.format(language=language), userPrompt, 0.3, userData)
        return response
    
    elif(token == p.TASK_PRE_5_HOOK):
        log.save_log("PRE_FOOD_HISTORY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.PRE_TASK_5_PROMPT.format(language=language), userPrompt, 0.3, userData)
        return response
    
    elif(token == p.TASK_PRE_6_HOOK):
        log.save_log("PRE_SUSTAINABILITY_EXPERT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.PRE_TASK_6_PROMPT.format(language=language), userPrompt, 0.3, userData)
        return response
    
    elif(token == p.TASK_PRE_7_HOOK):
        log.save_log("PRE_FOOD_DIARY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.PRE_TASK_7_PROMPT.format(language=language), userPrompt, 0.3, userData)
        return response

########################################################################################
# 2 FOOD SUGGESTION

    elif(token == p.TASK_2_HOOK):
        log.save_log("FOOD_SUGGESTION_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_2_PROMPT.format(language=language), userPrompt + ' ' + info, 0.1, userData)
        return response
    
    elif(token == p.TASK_2_05_HOOK):
        log.save_log("FOOD_SUGGESTION_DATA_VERIFICATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        json_mealdata_obj = jsonpickle.decode(info)

        #Meal type check and answer not managed by LLMS since it is straightforward
        if(json_mealdata_obj['mealType'] == None or json_mealdata_obj['mealType'] == ''):
            answer = lcs.translate_text(p.ASK_FOR_MEAL_TYPE, language) 
            action = p.TASK_2_HOOK           
            response = rc.Response(answer,action,info,None,'')
        else:
            action = p.TASK_2_10_HOOK
            response = rc.Response('',action,info,None,'')

        return response
    
    elif(token == p.TASK_2_10_HOOK):
        log.save_log("PROVIDING_FOOD_SUGGESTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        # call recommender system

        # traduciamo le informazioni sul suggerimento
        translated_info = lcs.translate_info(info, language)

        temp_suggestedRecipe = food.get_recipe_suggestion(translated_info,userData)
        suggestedRecipe = utils.adapt_output_to_bot(temp_suggestedRecipe)
        translated_info = utils.escape_curly_braces(translated_info)
        userDataStr = utils.escape_curly_braces(userData.to_json())

        userPrompt = "Suggest me a recipe given the following constraints " + translated_info

        if(suggestedRecipe != 'null'):

            # recuperiamo le informazioni sulla ricetta da suggerire
            nutritional_facts = rcpService.get_nutritional_facts_by_id(int(temp_suggestedRecipe.id))
            nutritional_facts = utils.escape_curly_braces(str(nutritional_facts))
            who_score = temp_suggestedRecipe.who_score

            allergies = user.get_allergies(userData.id)
            restrictions = user.get_restrictions(userData.id)
            evolving_diet = user.get_evolving_diet(userData.id)
            
            response = lcs.execute_chain(p.TASK_2_10_PROMPT.format(suggestedRecipe=suggestedRecipe, mealInfo=translated_info, userData=userDataStr, language = language, allergies=allergies, restrictions=restrictions, evolving_diet=evolving_diet, nutritional_facts=nutritional_facts, who_score=who_score), userPrompt, 0.6, userData, memory, True)
        else:
            response = lcs.execute_chain(p.TASK_2_10_1_PROMPT.format(mealInfo=translated_info, userData=userDataStr, language = language), userPrompt, 0.6, userData, memory, False)        
        
        return response
    
    elif(token == p.TASK_2_20_HOOK):
        log.save_log("SUGGESTION_CHAT_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_2_20_PROMPT.format(language=language), userPrompt, 0.6, userData, memory, True)
        return response
    
    elif(token == p.TASK_2_25_HOOK):

        log.save_log("SUGGESTION_SWAP_INGREDIENT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)

        originalPrompt = utils.de_escape_curly_braces(memory.messages[0].content)    
        jsonRecipe = utils.extract_json(originalPrompt, 0)
        ingredients_to_remove, ingredients_to_add = rcpService.get_substitutions_info(info)

        fhService.build_and_save_user_history(userData, jsonRecipe, "accepted", ingredients_to_remove, ingredients_to_add)
        fhService.clean_temporary_declined_suggestions(userData.id)

        answer = lcs.translate_text(p.CUSTOM_SUGGESTION_ACCEPTED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)

        return response
    
    elif(token == p.TASK_2_30_HOOK):
        log.save_log("SUGGESTION_ACCEPTED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"accepted")
        fhService.clean_temporary_declined_suggestions(userData.id)
        answer = lcs.translate_text(p.SUGGESTION_ACCEPTED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)

        return response
    
    elif(token == p.TASK_2_40_HOOK):
        log.save_log("SUGGESTION_DECLINED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"declined")
        fhService.clean_temporary_declined_suggestions(userData.id)
        answer = lcs.translate_text(p.SUGGESTION_DECLINED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        
        return response
    
    elif(token == p.TASK_2_50_HOOK):
        log.save_log("REQUIRED_ANOTHER_SUGGESTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"temporary_declined")
        originalUserPrompt = memory.messages[1].content
        response = rc.Response('',"TOKEN 1",'',None,originalUserPrompt)
        
        return response
    

########################################################################################
# 3 RECIPE SUSTAINABILITY EXPERT

    elif(token == p.TASK_3_HOOK):
        log.save_log("EXPERT_HUB", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_PROMPT, userPrompt, 0.1, userData)
        return response
    
    elif(token == p.TASK_3_10_HOOK):
        log.save_log("RECIPE_IMPROVEMENT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_10_PROMPT.format(language=language), userPrompt+' '+info, 0.1, userData)
        return response
    
    elif(token == p.TASK_3_15_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_INGREDIENT_LIST_EVALUATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_15_PROMPT.format(language=language), userPrompt, 0.1, userData)
        #recover the previous info because the prompt do not generate new info
        response.info = info
        return response
    
    elif(token == p.TASK_3_20_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_EXECUTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        #call the recipe improvement service

        translated_info = lcs.translate_info(info, language)

        baseRecipe = imp.get_base_recipe(translated_info)
        improvedRecipe = imp.get_recipe_improved(baseRecipe,userData)
        
        base_ingredient_list = []
        for ingredient in baseRecipe.ingredients:
            base_ingredient_list.append(ingredient.name)
        
        imp_ingredient_list = []
        for ingredient in improvedRecipe.ingredients:
            imp_ingredient_list.append(ingredient.name)

        result_ingredient = list(set(base_ingredient_list + imp_ingredient_list))

        # filtra eventuali messaggi vuoti : caso in cui l'utente chiede un altro miglioramento ma considerando la stessa ricetta
        if memory is not None:
            memory.messages = [m for m in memory.messages if m.content and m.content.strip()]
  
        if(improvedRecipe != 'null'):
            
            # recupera le fonti degli ingredienti usati
            ingredients_data_origins = {}
            sueatablelife_link = "https://doi.org/10.6084/m9.figshare.13271111.v2"

            for ingredient in result_ingredient:
                ingredientDataOrigin = ingService.get_data_origin(ingredient)
                if ingredientDataOrigin != None:
                    ingredients_data_origins[ingredient] = ingredientDataOrigin
                else :
                    ingredients_data_origins[ingredient] = sueatablelife_link
        
            # recuperiamo le informazioni sulla ricetta da suggerire
            nutritional_facts = rcpService.get_nutritional_facts_by_id(int(improvedRecipe.id))
            nutritional_facts = utils.escape_curly_braces(str(nutritional_facts))

            ingredients_data_origins = utils.adapt_output_to_bot(ingredients_data_origins)

            response = lcs.execute_chain(p.TASK_3_20_PROMPT.format(baseRecipe=utils.adapt_output_to_bot(baseRecipe), improvedRecipe=utils.adapt_output_to_bot(improvedRecipe), language=language, ingredients_data_origins=ingredients_data_origins, nutritional_facts=nutritional_facts), userPrompt, 0.1, userData, memory, True)
        else:
            None
            userDataStr = utils.escape_curly_braces(userData.to_json())
            response = lcs.execute_chain(p.TASK_3_20_1_PROMPT.format(baseRecipe=utils.adapt_output_to_bot(baseRecipe), userData=userDataStr, language=language), userPrompt, 0.1, userData)
        return response
    
    elif(token == p.TASK_3_30_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_CHAT_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_3_30_PROMPT.format(language=language), userPrompt, 0.6, userData, memory, True)
        return response
    
    elif(token == p.TASK_3_35_HOOK):

        log.save_log("RECIPE_IMPROVEMENT_SWAP_INGREDIENT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)

        originalPrompt = utils.de_escape_curly_braces(memory.messages[0].content)
        jsonRecipe = utils.extract_json(originalPrompt, 1)
        ingredients_to_remove, ingredients_to_add = rcpService.get_substitutions_info(info)

        fhService.build_and_save_user_history(userData, jsonRecipe, "accepted", ingredients_to_remove, ingredients_to_add)
        fhService.clean_temporary_declined_suggestions(userData.id)

        answer = lcs.translate_text(p.CUSTOM_RECIPE_IMPROVEMENT_ACCEPTED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)

        return response
    
    # ricetta migliorata accettata direttamente
    elif(token == p.TASK_3_40_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_ACCEPTED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        #save the improved recipe as consumed by the user since she will have to eat it
        manage_suggestion(userData,memory,"accepted",1)
        fhService.clean_temporary_declined_suggestions(userData.id)
        answer = lcs.translate_text(p.RECIPE_IMPROVEMENT_ACCEPTED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        return response
    
    elif(token == p.TASK_3_50_HOOK):
        log.save_log("RECIPE_IMPROVEMENT_DECLINED", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        #don't save the rejected recipe, this because this don't have to be considered as a suggestion? i'm thinking about it
        manage_suggestion(userData,memory,"declined")
        fhService.clean_temporary_declined_suggestions(userData.id)
        answer = lcs.translate_text(p.RECIPE_IMPROVEMENT_DECLINED, language)
        response = rc.Response(answer,"TOKEN 1",'',None,p.USER_GREETINGS_PHRASE)
        return response
    
    elif(token == p.TASK_3_60_HOOK):
        log.save_log("REQUIRED_ANOTHER_RECIPE_IMPROVEMENT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        manage_suggestion(userData,memory,"temporary_declined",1)
        originalUserPrompt = memory.messages[1].content
        response = rc.Response('',"TOKEN 3.10",'',None,originalUserPrompt)
        return response
    
########################################################################################
# 4 USER PROFILE RECAP AND UPDATE

    elif(token == p.TASK_4_HOOK):
        log.save_log("PROFILE_SUMMARY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        userPrompt = p.USER_PROMPT.format(user_data=userData.to_json())
        response = lcs.execute_chain(p.TASK_4_PROMPT.format(language=language), userPrompt, 0.8, userData)
        return response
    
    elif(token == p.TASK_4_10_HOOK):
        log.save_log("ASKING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_4_10_PROMPT.format(language=language), userPrompt, 0.1, userData)
        return response
    
    elif(token == p.TASK_4_20_HOOK):
        log.save_log("PRESENTING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_4_20_PROMPT.format(language=language), userPrompt, 0.1, userData)
        return response
    
    elif(token == p.TASK_4_30_HOOK):
        log.save_log("PERFORMING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_4_30_PROMPT.format(language=language), "User data: "+ userPrompt, 0.1, userData)
        return response
    
    elif(token == p.TASK_4_40_HOOK):
        log.save_log("EVALUATING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)

        translated_info = lcs.translate_info(info, language)
        userData.update_from_json(translated_info)

        response = lcs.execute_chain(p.TASK_4_40_PROMPT.format(language=language), "User data: " + userData.to_json() + " "+ userPrompt, 0.1, userData)
        return response
    
    elif(token == p.TASK_4_50_HOOK):
        log.save_log("PERSISTING_PROFILE_UPDATE", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        #persist user data calling MongoDB...
        response = lcs.execute_chain(p.TASK_4_50_PROMPT.format(language=language), "User data: " + userData.to_json(), 0.1, userData)
        user.update_user(userData)
        return response
    
########################################################################################
# 5 HISTORY RETRIEVAL

    elif(token == p.TASK_5_HOOK):
        log.save_log("FOOD_HISTORY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_5_PROMPT.format(language=language), userPrompt, 0.3, userData)
        return response
    
    # WEEK 
    elif(token == p.TASK_5_01_HOOK):
        log.save_log("FOOD_HISTORY_WEEK", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        foodHistory = utils.adapt_output_to_bot(history.get_user_history_of_week(userData.id))

        #not managed by LLMS since it is straightforward
        action = p.TASK_5_05_HOOK
        print(f"TOKEN : {token} -----> {action}")
        response = lcs.execute_chain(p.TASK_5_05_PROMPT.format(food_history=foodHistory, language=language), userPrompt, 0.3, userData, memory, True)
        return response
        
    # MONTH
    elif(token == p.TASK_5_02_HOOK):
        log.save_log("FOOD_HISTORY_MONTH", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        foodHistory = utils.adapt_output_to_bot(history.get_user_history_of_month(userData.id))

        #not managed by LLMS since it is straightforward
        action = p.TASK_5_05_HOOK
        print(f"TOKEN : {token} -----> {action}")
        response = lcs.execute_chain(p.TASK_5_05_PROMPT.format(food_history=foodHistory, language=language), userPrompt, 0.3, userData, memory, True)
        return response
    
    # CUSTOM DATE
    elif(token == p.TASK_5_03_HOOK):
        log.save_log("FOOD_HISTORY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        begin_date, end_date = history.get_custom_dates(info)
        foodHistory = utils.adapt_output_to_bot(history.get_user_history_of_custom_date(userData.id, begin_date, end_date))
        
        #not managed by LLMS since it is straightforward
        action = p.TASK_5_05_HOOK
        print(f"TOKEN : {token} -----> {action}")
        response = lcs.execute_chain(p.TASK_5_05_PROMPT.format(food_history=foodHistory, language=language), userPrompt, 0.3, userData, memory, True)
        return response
    
    elif(token == p.TASK_5_10_HOOK):
        log.save_log("FOOD_HISTORY_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_5_10_PROMPT.format(language=language), userPrompt, 0.3, userData, memory, True)
        if response.action == p.TASK_MINUS_1_HOOK:
            response.modifiedPrompt = p.USER_GREETINGS_PHRASE
        return response
    
########################################################################################
# 6 SUSTAINABILITY EXPERT

    elif(token == p.TASK_6_HOOK):
        log.save_log("SUSTAINABILITY_EXPERT", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_6_PROMPT, userPrompt, 0.2, userData)
        return response
    
    elif(token == p.TASK_6_10_HOOK):
        log.save_log("SUSTAINABILITY_CONCEPT_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        allergies = user.get_allergies(userData.id)
        restrictions = user.get_restrictions(userData.id)
        
        concept = lcs.translate_concept(userPrompt,language)

        response = ws.web_search(p.WEB_SEARCH_PROMPT.format(concept = concept), concept, 0.2, userData, None, True)

        clean_answer = response.answer['clean_answer']
        citations_and_urls = response.answer['citations_and_urls']
        citations_and_urls = utils.escape_curly_braces(str(citations_and_urls))

        response = lcs.execute_chain(p.TASK_6_10_PROMPT.format(concept = concept, language=language, clean_answer = clean_answer, allergies = allergies, restrictions = restrictions, citations_and_urls = citations_and_urls), userPrompt, 0.3, userData, memory, True)
        
        return response
    
    elif(token == p.TASK_6_20_HOOK):
        log.save_log("SUSTAINABILITY_INGREDIENTS_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        allergies = user.get_allergies(userData.id)
        restrictions = user.get_restrictions(userData.id)
        ingredientsData = jsonpickle.decode(info)

        translated_ingredients = lcs.translate_ingredients_list(ingredientsData['ingredients'],language)

        # recupera le fonti
        ingredients_data_origins = {}

        #sueatablelife_link = "https://www.sueatablelife.eu/"
        sueatablelife_link = "https://doi.org/10.6084/m9.figshare.13271111.v2"

        for ingredient in translated_ingredients:
            ingredientDataOrigin = ingService.get_data_origin(ingredient)
            if ingredientDataOrigin != None:
                ingredients_data_origins[ingredient] = ingredientDataOrigin
            else :
                ingredients_data_origins[ingredient] = sueatablelife_link
        

        ingredients_data_origins = utils.adapt_output_to_bot(ingredients_data_origins)
        ingredientsData = utils.adapt_output_to_bot(ingService.get_ingredient_list_from_generic_list_of_string(translated_ingredients))
        
        # filtra eventuali messaggi vuoti
        # Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'messages.3: all messages must have non-empty content except for the optional final assistant message'}}
        if memory is not None:
            memory.messages = [m for m in memory.messages if m.content and m.content.strip()]
            
        response = lcs.execute_chain(p.TASK_6_20_PROMPT.format(ingredients = ingredientsData, language=language, allergies = allergies, restrictions = restrictions, ingredients_data_origins=ingredients_data_origins), userPrompt, 0.3, userData, memory, True)
        return response
    
    elif(token == p.TASK_6_25_HOOK):
        log.save_log("HEALTHNIESS_INGREDIENTS_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        allergies = user.get_allergies(userData.id)
        restrictions = user.get_restrictions(userData.id)
        ingredientsData = jsonpickle.decode(info)

        translated_ingredients = lcs.translate_ingredients_list(ingredientsData['ingredients'],language)    

        ingredientsData = ingService.get_nutritional_facts_from_list_of_ingredients(translated_ingredients)
        ingredientsData = utils.adapt_output_to_bot(ingredientsData)

        data_origin = "https://calorieninjas.com/"

        # filtra eventuali messaggi vuoti
        # Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'messages.3: all messages must have non-empty content except for the optional final assistant message'}}
        if memory is not None:
            memory.messages = [m for m in memory.messages if m.content and m.content.strip()]
            
        response = lcs.execute_chain(p.TASK_6_25_PROMPT.format(ingredients = ingredientsData, language=language, allergies = allergies, restrictions = restrictions, data_origin = data_origin), userPrompt, 0.3, userData, memory, True)
        return response
    
    elif(token == p.TASK_6_30_HOOK):
        log.save_log("SUSTAINABILITY_RECIPE_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        allergies = user.get_allergies(userData.id)
        restrictions = user.get_restrictions(userData.id)
        recipesData = jsonpickle.decode(info)

        recipes = er.extractRecipes(recipesData)
    
        ingredients_data_origins = {}
        sueatablelife_link = "https://doi.org/10.6084/m9.figshare.13271111.v2"
        
        for recipe_obj, nutritional_facts in recipes:
            for ingredient in recipe_obj.ingredients:
                ingredientDataOrigin = ingService.get_data_origin(ingredient.name)
                if ingredientDataOrigin != None:
                    ingredients_data_origins[ingredient.name] = ingredientDataOrigin
                else :
                    ingredients_data_origins[ingredient.name] = sueatablelife_link
        
        ingredients_data_origins = utils.adapt_output_to_bot(ingredients_data_origins)

        recipes = utils.adapt_output_to_bot(recipes)
        response = lcs.execute_chain(p.TASK_6_30_PROMPT.format(recipes = recipes, language=language, allergies = allergies, restrictions = restrictions, ingredients_data_origins =ingredients_data_origins), userPrompt, 0.3, userData, memory, True)
        return response
    
    elif(token == p.TASK_6_35_HOOK):
        log.save_log("HEALTHINESS_RECIPE_EXPERT_INTERACTION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        allergies = user.get_allergies(userData.id)
        restrictions = user.get_restrictions(userData.id)
        recipesData = jsonpickle.decode(info)

        recipes = er.extractRecipes(recipesData)
        recipes = utils.adapt_output_to_bot(recipes)

        response = lcs.execute_chain(p.TASK_6_35_PROMPT.format(recipes = recipes, language=language, allergies = allergies, restrictions = restrictions), userPrompt, 0.3, userData, memory, True)
        return response
    
    elif(token == p.TASK_6_40_HOOK):
        log.save_log("SUSTAINABILITY_EXPERT_LOOP", datetime.datetime.now(), "System", userData.id, PRINT_LOG)

        response = lcs.execute_chain(p.TASK_6_40_PROMPT.format(language=language),userPrompt, 0.3, userData, memory, True)
        if response.action == p.TASK_MINUS_1_HOOK:
            response.modifiedPrompt = p.USER_GREETINGS_PHRASE

        return response
    
########################################################################################
# 7 RECIPE CONSUPTION DIARY

    elif(token == p.TASK_7_HOOK):
        log.save_log("RECIPE_CONSUPTION_DIARY", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_7_PROMPT.format(language=language), "Meal data: " + info +" "+userPrompt, 0.2, userData)
        return response
    
    elif(token == p.TASK_7_10_HOOK):
        log.save_log("RECIPE_CONSUPTION_DIARY_DATA_VERIFICATION", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        response = lcs.execute_chain(p.TASK_7_10_PROMPT.format(language=language), "Meal data: " + info, 0.3, userData)
        return response
    
    elif(token == p.TASK_7_20_HOOK):
        log.save_log("RECIPE_CONSUPTION_DIARY_DATA_SAVING", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        
        jsonRecipeAssertion = utils.extract_json(info, 0)

        """
        jsonRecipeAssertion :  {
                "mealType": "Lunch",
                "ingredients": ["pasta", "chicken", "spinach", "olive oil"],
                "quantities": [80, 150, 100, 10],
                "name": "Pasta with chicken and spinach"
        }
        """

        fhService.build_and_save_user_history_from_user_assertion(userData, jsonRecipeAssertion)

        response = lcs.execute_chain(p.TASK_7_20_PROMPT.format(language=language), "Meal data: " + jsonRecipeAssertion, 0.1, userData)
        return response
    
########################################################################################
# loop states - X

    # la memoria viene ripulita passando None come memoria della risposta

    elif(token == p.TASK_MINUS_2_HOOK):
        log.save_log("MEMORY_CLEANING_BEFORE_2", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        fhService.clean_temporary_declined_suggestions(userData.id)
        # passiamo le informazioni sulla ricetta da suggerire tramite info
        return rc.Response('',"TOKEN 2",info, None,'')
    
    elif(token == p.TASK_MINUS_3_10_HOOK):
        log.save_log("MEMORY_CLEANING_BEFORE_3_10", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        fhService.clean_temporary_declined_suggestions(userData.id)
        # passiamo le informazioni sulla ricetta da migliorare tramite info
        return rc.Response('',"TOKEN 3.10",info, None,'')

    elif(token == p.TASK_MINUS_4_HOOK):
        log.save_log("MEMORY_CLEANING_BEFORE_4", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        fhService.clean_temporary_declined_suggestions(userData.id)
        return rc.Response('',"TOKEN 4",'',None,'')
    
    elif(token == p.TASK_MINUS_5_HOOK):
        log.save_log("MEMORY_CLEANING_BEFORE_5", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        fhService.clean_temporary_declined_suggestions(userData.id)
        return rc.Response('',"TOKEN 5",'',None,'')
        
    elif(token == p.TASK_MINUS_6_HOOK):
        log.save_log("MEMORY_CLEANING_BEFORE_6", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        fhService.clean_temporary_declined_suggestions(userData.id)
        # passiamo le informazioni all'esperto
        return rc.Response('',"TOKEN 6",info,None,'')
           
    elif(token == p.TASK_MINUS_7_HOOK):
        log.save_log("MEMORY_CLEANING_BEFORE_7", datetime.datetime.now(), "System", userData.id, PRINT_LOG)
        fhService.clean_temporary_declined_suggestions(userData.id)
        # passiamo le informazioni sul pasto consumato dall'utente
        return rc.Response('',"TOKEN 7",info, None,'')
    
########################################################################################


    print("\n----------------------------------------------------------------------------------------------------")


def manage_suggestion(userData,memory,status,whichJson=0):
    """
    Aggiorna lo stato del suggerimento alimentare proposto all'utente, e lo salva nel db.

    Args : 
    - userData : dati utente
    - memory : memoria conversazionale
    - status : stato di accettazione dela ricetta
    - whichJson : indice del json nel quale è contenuta la ricetta
    """
    originalPrompt = utils.de_escape_curly_braces(memory.messages[0].content)
    jsonRecipe = utils.extract_json(originalPrompt, whichJson)
    fhService.build_and_save_user_history(userData, jsonRecipe, status)


def manage_last_interaction(userData):
    """
    Aggiorna l'ultima interazione che l'utente ha avuto con il chatbot nel db.

    Args : 
    - userData : dati utente, contenenti l'id dell'utente di cui aggiornare l'ultima interazione
    """
    userData.lastInteraction = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user.update_user_last_interaction(userData.id, userData.lastInteraction)