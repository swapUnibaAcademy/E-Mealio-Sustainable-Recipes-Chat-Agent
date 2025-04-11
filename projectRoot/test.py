import unittest
import ChatbotController as cc
import Constants as con
import dto.User as ud
import persistence.UserPersistence as up
import persistence.UserHistoryPersistence as uhp
import jsonpickle
#All the test must be passed both from OPENAI and ANTHROPIC models to ensure full compatibility with both versions of the bot.


#OPENAI OK
#ANTHROPIC OK
class Test1ControllerHub(unittest.TestCase):
    #HUB TESTS
    def test1_greetings(self):
        print("answer_router: Test Greetings")
        response = cc.answer_router(get_user_data(),con.USER_GREETINGS_PHRASE,con.TASK_1_HOOK,"","")
        print_answers(response)
        #check if the generated token is equal to the expected token, that info are empty and the answer is not empty
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
        #this means that the bot has greeted the user
    #HUB-> HUB (Unrelated message)
    def test2_greetings_2(self):
        print("answer_router: Test Greetings with Unrelated Message")
        response = cc.answer_router(get_user_data(),"What time is it?",con.TASK_1_HOOK,"","")
        print_answers(response)
        #check if the generated token is equal to the expected token, that info are empty and the answer is not empty
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
        #this means that the bot has greeted the user
    #HUB-> HUB (Explaining recommendation)
    def test3_bot_explaining_itself_recommendation(self):
        print("answer_question: Explanation of Recommendation")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can you recommend recipes?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
    #HUB-> HUB (Explaining improvements)
    def test4_bot_explaining_itself_improvements(self):
        print("answer_question: Explanation of Improvements")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can you improve recipes?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
    #HUB-> HUB (Explaining expert)
    def test5_bot_explaining_itself_expert(self):
        print("answer_question: Explanation of Expertise")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can you provide information about sustainability concepts?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
    #HUB-> HUB (Explaining profile)
    def test6_bot_explaining_itself_profile(self):
        print("answer_question: Explanation of Profile")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can you update my profile?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
    #HUB-> HUB (Explaining history)
    def test7_bot_explaining_itself_history(self):
        print("answer_question: Explanation of History")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can you analize my food history of the week?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
        #HUB-> HUB (Explaining assertion)
    def test8_bot_explaining_itself_assertion(self):
        print("answer_question: Explanation of Assetion")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can you register my food consuption?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(response.info, ' ')
        self.assertTrue(len(response.answer) > 0)
    #HUB -> RECOMMENDATION
    def test9_from_hub_to_recommendation_entry_point(self):
        print("answer_question: Test Recommendation Presentation")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"What can I eat today?",con.TASK_1_HOOK,"","")
        print_answers(response)
        #the hub moves to the recommendation task
        self.assertEqual(response.action, con.TASK_2_HOOK)
        #info data not produced 
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test10_from_hub_to_expert_improvement(self):
        print("answer_question: Expert Hub Entry Point")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can I improve the sustainability of a pizza?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the recommendation task
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB 2
    def test11_from_hub_to_expert_improvement_2(self):
        print("answer_question: Expert Hub Entry Point 2")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"How can I improve the sustainability of a pizza made of dough, mozzarella, tomato and basil?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the recommendation task
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test12_from_hub_to_expert_ingredients(self):
        print("answer_question: Expert Hub Entry Point; Ingredient Expert")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"Tell me about the sustainability of bananas and pineapples.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test13_from_hub_to_expert_recipe(self):
        print("answer_question: Expert Hub Entry Point; Recipe Expert")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"Compare the sustainability of a Veggie Lasagna, with a Pasta Carbonara",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test14_from_hub_to_expert_recipe_with_ingredients(self):
        print("answer_question: Expert Hub Entry Point; Recipe Expert with ingredients")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"Compare the sustainability of a Sandwich made of bread, tuna, salad, mayonaise and cheese, with a Pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB -> EXPERT HUB
    def test15_from_hub_to_expert_concept(self):
        print("answer_question: Expert Hub Entry Point; Concept Expert")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"What is climate change?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_3_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB-> FOOD ASSERTION
    def test16_from_hub_to_food_assertion(self):
        print("answer_question: Food Assertion Entry Point")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"I've eat a pizza.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_7_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB-> PROFILE RECAP
    def test17_from_hub_to_profile_recap(self):
        print("answer_question: Profile Recap Entry Point")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_4_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)
    #HUB-> FOOD HISTORY
    def test18_from_hub_to_food_history(self):
        print("answer_question: Food History Entry Point")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"Can you resume my food history?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the hub moves to the expert hub
        self.assertEqual(response.action, con.TASK_5_HOOK)
        #info data not produced
        self.assertTrue(response.info.strip() == '')
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)


#OPENAI OK
#ANTHROPIC OK
class Test2ControllerRegistration(unittest.TestCase):
#USER REGISTRATION TESTS
    def test1_user_registration_entry_point(self):
        print("answer_question: Test User Registration Presentation")
        userData = get_user_data()
        response = cc.answer_question(userData,"Hello",con.TASK_0_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        #info data not produced because the system is asking for the user data
        self.assertTrue(response.info.strip() == '')
        self.assertTrue(len(response.answer) > 0)

    def test2_user_registration_unrelated_message(self):
        print("answer_question: Test User Registration Presentation: Unrelated Message")
        userData = get_user_data()
        response = cc.answer_question(userData,"What time is it?",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        #info data not produced because the system is replyng to a not compliant message
        self.assertTrue(response.info.strip() == '')
        self.assertTrue(len(response.answer.strip()) != 0)

    def test3_user_registration_partial_data(self):
        print("answer_question: Test User Registration Presentation: Partial Data Provided")
        userData = get_user_data()
        response = cc.answer_question(userData,"Hello, I'm Giacomo Rossi.",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_2_HOOK)
        #info data produced but incomplete
        self.assertTrue(response.info.strip() != '')
        userDataObtained = jsonpickle.decode(response.info)
        #check if the data is correct
        self.assertEqual(userDataObtained['name'], "Giacomo")
        self.assertEqual(userDataObtained['surname'], "Rossi")
        self.assertEqual(userDataObtained['dateOfBirth'], "")        
        #answer empty becuase the response is a change of inner state, is not for the user
        self.assertTrue(len(response.answer) == 0)

    def test4_user_registration_all_mandatory_data(self):
        print("answer_router: Test User Registration Presentation: All Mandatory Data Provided")
        userData = get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990.",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        #user data object is updated with the provided data
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.allergies,[])
        self.assertEqual(userData.restrictions, [])

    def test5_user_registration_not_all_mandatory_data_and_unrelated_response(self):
        print("answer_router: Test User Registration Presentation: All Mandatory Data Provided")
        userData = get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy.",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"What do you want??",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"I born the first of january 1990",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)

        #user data object is updated with the provided data
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.allergies,[])
        self.assertEqual(userData.restrictions, [])

    def test6_user_registration_all_mandatory_and_optional_data(self):
        print("answer_router: Test User Registration Presentation: All Mandatory and Optiona Data Provided")
        userData = get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990. Im allergic to peanut and fish. I Follow a vegan diet.",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        #check if the allergies are in the list
        self.assertTrue("peanut" in userData.allergies)
        self.assertTrue("fish" in userData.allergies)
        self.assertTrue("vegan" in userData.restrictions)

    def test7_user_registration_multistep_with_reminder_consent(self):
        print("multistep answer_router: Test User Registration Presentation: All Mandatory Data Provided; Then Provide Reminder Consent")
        userData = get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy on 01/01/1990.",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.allergies,[])
        self.assertEqual(userData.restrictions, [])
        response = cc.answer_router(userData,"Yes I want reminders",con.TASK_0_4_HOOK,"",None)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(userData.reminder, True)

    def test8_user_registration_multistep_with_negate_reminder_consent(self):
        print("multistep answer_router: Test User Registration Presentation: All Mandatory Data Provided, But In Two Step; Then Negate Reminder Consent")
        userData = get_user_data()
        response = cc.answer_router(userData,"Hello, I'm Giacomo Rossi, born in Italy.",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_1_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.nation, "Italy")
        self.assertEqual(userData.dateOfBirth, "")
        self.assertEqual(userData.allergies,[])
        self.assertEqual(userData.restrictions, [])

        response = cc.answer_router(userData,"I was born on 01/01/1990, i'm also allergic to peanuts.",con.TASK_0_1_HOOK,"",None)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_0_4_HOOK)
        self.assertTrue(len(response.answer) > 0)
        self.assertEqual(userData.name, "Giacomo")
        self.assertEqual(userData.surname, "Rossi")
        self.assertEqual(userData.dateOfBirth, "01/01/1990")
        self.assertEqual(userData.nation, "Italy")
        self.assertTrue("peanut" in userData.allergies)
        self.assertEqual(userData.restrictions, [])

        response = cc.answer_router(userData,"No thanks.",con.TASK_0_4_HOOK,"",None)
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertEqual(userData.reminder, False)

    #run after all the tests
    def tearDown(self):
        up.delete_user_by_user_id("0")
        uhp.delete_user_history("0")
        print("Test completed")


#OPENAI OK
#ANTHROPIC OK
class Test3ControllerRecommendation(unittest.TestCase):
#RECOMMENDATION TESTS
    def test1_recommendation_move_to_data_verification(self):
        print("answer_question: Test Recommendation Presentation; Move to Data Verification")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"What can I eat?",con.TASK_2_HOOK,None,"")
        print_answers(response)
        #moves to data verification state
        self.assertEqual(response.action, con.TASK_2_05_HOOK)
        #info data produced
        self.assertTrue(response.info.strip() != '')
        jsonMealdataObj = jsonpickle.decode(response.info)
        self.assertTrue(len(jsonMealdataObj['mealType'])==0)
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)

    def test2_recommendation_move_to_data_verification_with_meal_type(self):
        print("answer_question: Test Recommendation Presentation; Move to Data Verification with Meal Type")
        userData = get_valid_user_data()
        response = cc.answer_question(userData,"What can I eat for dinner?",con.TASK_2_HOOK,None,"")
        print_answers(response)
        #moves to data verification state
        self.assertEqual(response.action, con.TASK_2_05_HOOK)
        #info data produced
        self.assertTrue(response.info.strip() != '')
        jsonMealdataObj = jsonpickle.decode(response.info)
        self.assertTrue(jsonMealdataObj['mealType']=="Dinner")
        #answer is empty because is a state change
        self.assertTrue(len(response.answer) == 0)

    def test3_reccomentation_with_answer(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

    def test4_reccomentation_with_no_suggestion(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided But No Suggestions")
        userData = get_valid_user_data_with_impossible_constraints()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to hub after no suggestion
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

    def test5_reccomentation_with_answer_conversation_and_acceptance(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Mhh, can you suggest me something else?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        #Why this is a good recipe for me?
        #Can you list the ingredients involved?
        #Are the ingredients sustainable?
        #Ok thak you, i'll eat this one.

        response = cc.answer_router(userData,"Why this is a good recipe for me?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you list the ingredients involved?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"Are the ingredients sustainable?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"Ok thank you, i'll eat this one.",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m glad you accepted my suggestion! If I can help you with other food sustainability questions, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test6_reccomentation_with_ingredients_answer_conversation_and_acceptance(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"Suggest me something to eat that contains rice?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_HOOK)
        #answer provided, it is asking for the meal type
        self.assertTrue(len(response.answer) > 0)
        #info is not empty, it contains the meal information, in this case the ingredient
        self.assertTrue(response.info.strip() != '')
        mealData = jsonpickle.decode(response.info)
        self.assertTrue("rice" in mealData['ingredients_desired'])
        response = cc.answer_router(userData,"It is for lunch.",con.TASK_2_HOOK,response.memory,"")
        print_answers(response)
        #moves again to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Ok thank you, i'll eat this one.",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m glad you accepted my suggestion! If I can help you with other food sustainability questions, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test7_reccomentation_with_answer_and_refutation(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"No thanks, I don't like it.",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m sorry you didn\'t accepted my suggestion. I hope you will find something for you next time! If I can help you with other food sustainability answer, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test8_reccomentation_with_answer_and_unrelated_question(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided But Unrelated")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"What time is it?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves to memory cleaning state
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

    def test9_reccomentation_with_answer_and_unrelated_recipe(self):
        print("answer_router: Test Recommendation Presentation: Answer Provided But Unrelated Recipe")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What can I eat for dinner?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe suggestion loop state
        self.assertEqual(response.action, con.TASK_2_20_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty, here the answer is already provided
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"And what about Banana Split?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves to memory cleaning state
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

    #run after all the tests
    def tearDown(self):
        uhp.delete_user_history("0")
        print("Test completed")


#OPENAI OK
#ANTHROPIC OK
class Test4ControllerRecipeImprovements(unittest.TestCase):
#RECIPE IMPROVEMENT TESTS
    def test1_recipe_improvement_with_answer_change_and_acceptance(self):
        print("answer_router: Test Recipe Improvement Presentation: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"How can I improve the sustainability of a greek sandwich?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to ingredient acquisition state
        self.assertEqual(response.action, con.TASK_3_15_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is not empty
        self.assertTrue(response.info.strip() != '')

        response = cc.answer_router(userData,"What do you want?.",con.TASK_3_15_HOOK,None,response.info)
        print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_15_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is not empty
        self.assertTrue(response.info.strip() != '')

        response = cc.answer_router(userData,"It was made of bread, yogurt and onion.",con.TASK_3_15_HOOK,None,response.info)
        print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you suggest me an alternative?",con.TASK_3_30_HOOK,response.memory,"")
        print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Yes, I'll try it.",con.TASK_3_30_HOOK,response.memory,"")
        print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, "I'm glad you accepted my improved version of the recipe! If I can help you with other food sustainability questions, I'm here to help!")
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test2_recipe_improvement_with_ingredients_refutation(self):
        print("answer_router: Test Recipe Improvement Presentation: Refutation")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"How can I improve the sustainability of a pizza made of pizza dough, mozzarella and tomato?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"No thanks, I don't like it.",con.TASK_3_30_HOOK,response.memory,"")
        print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #answer provided
        self.assertEqual(response.answer, 'I\'m sorry you didn\'t accepted my improved version of the recipe. If I can help you with other food sustainability answer, I\'m here to help!')
        #exiting from a loop generate a callaback
        self.assertTrue(len(response.modifiedPrompt)>0)

    def test3_recipe_improvement_with_ingredients_conversation(self):
        print("answer_router: Test Recipe Improvement Presentation: Question about recipe")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"How can I improve the sustainability of a pizza made of pizza dough, mozzarella and tomato?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you list the ingredients involved in the improved recipe?",con.TASK_3_30_HOOK,response.memory,"")
        print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"Can you provide the sustainability of each ingredients?",con.TASK_3_30_HOOK,response.memory,"")
        print_answers(response)
        #moves to the hub
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

    def test4_recipe_improvement_with_ingredients_unrelated_conversation(self):
        print("answer_router: Test Recipe Improvement Presentation: unrelatred questions")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"How can I improve the sustainability of a pizza made of pizza dough, mozzarella and tomato?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"What time is it?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves to memory cleaning state
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)

    def test5_recipe_improvement_with_ingredients_unrelated_recipe_question(self):
        print("answer_router: Test Recipe Improvement Presentation: unrelatred questions")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"How can I improve the sustainability of a pizza made of pizza dough, mozzarella and tomato?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to recipe improvement loop state
        self.assertEqual(response.action, con.TASK_3_30_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"And what about Banana Split?",con.TASK_2_20_HOOK,response.memory,"")
        print_answers(response)
        #moves to memory cleaning state
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)

    #run after all the tests
    def tearDown(self):
        uhp.delete_user_history("0")
        print("Test completed")


#OPENAI OK
#ANTHROPIC OK
class Test5ControllerExpert(unittest.TestCase):
#INGREDIENT EXPERT TEST
    def test1_ingredient_expert_with_answer(self):
        print("answer_router: Test Ingredient Expert: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"Tell me about the sustainability of bananas and pineapples.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Why pineapples have more co2 emissions?",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Ok thanks!",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0)

#RECIPE EXPERT TEST   
    def test2_recipe_expert_with_answer(self):
        print("answer_router: Test Recipe Expert: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"Compare the sustainability of a Veggie Lasagna, with a Pasta Carbonara.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you resume the ingredients of both recipe explaining their sustainability?",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"Ok clear!",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0)   
 
#RECIPE EXPERT TEST WITH EXPLICIT INGREDIENTS
    def test3_recipe_expert_and_ingredients_with_answer(self):
        print("answer_router: Test Recipe Expert with Ingredients: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"Compare the sustainability of a Sandwich made of bread, tuna, salad, mayonaise and cheese, with a Pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Can you resume the ingredients of both recipe explaining their sustainability?",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"Ok thanks.",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0)  

#CONCEPT EXPERT TEST
    def test4_concept_expert_with_answer(self):
        print("answer_router: Test Concept Expert: Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What is cilmate change?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Is meat a problem in this context?",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"Ok, thank you for the information.",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0) 

    def test5_concept_expert_with_unrelated_answer(self):
        print("answer_router: Test Concept Expert: Unrelated Answer Provided")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What is Global Warming?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Are livestocks a problem in this context?",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"What time is it?",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0) 

    def test6_concept_expert_with_unrelated_answer_2(self):
        print("answer_router: Test Concept Expert: Unrelated Answer Provided 2")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What is Global Warming?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #moves to ingredient expert loop state
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')

        response = cc.answer_router(userData,"Are livestocks a problem in this context?",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        
        response = cc.answer_router(userData,"Tell me about pizza.",con.TASK_6_40_HOOK,response.memory,"")
        print_answers(response)
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #answer provided
        self.assertTrue(len(response.answer) > 0)
        #info is empty
        self.assertTrue(response.info.strip() == '')
        #exiting from a loop generate a callback
        self.assertTrue(len(response.modifiedPrompt)>0) 


#OPENAI OK
#ANTHROPIC OK
class Test6ControllerFoodAssertion(unittest.TestCase):
#FOOD ASSERTION TEST
    def test1_from_food_assertion_without_ingredients(self):
        print("answer_question: Food Assertion without Ingredients")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"I've eat a pizza.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #given the absence of ingredients, the system moves to the food diary state asking for the ingredients
        self.assertEqual(response.action, con.TASK_7_HOOK)
        #info data of the recipe produced
        self.assertTrue(response.info.strip() != '')
        #answer is asking for the ingredients
        self.assertTrue(len(response.answer) > 0)
        
        response = cc.answer_router(userData,"The pizza was made of pizza dough, tomato, mozzarella and basil.",con.TASK_7_HOOK,None,response.info)
        print_answers(response)
        #given the absence of meal type, the system moves to the food diary state asking for the ingredients
        self.assertEqual(response.action, con.TASK_7_HOOK)
        #info data of the recipe produced
        self.assertTrue(response.info.strip() != '')
        #answer is asking for the meal type
        self.assertTrue(len(response.answer) > 0)
        

        response = cc.answer_router(userData,"The pizza was for lunch.",con.TASK_7_HOOK,None,response.info)
        print_answers(response)
        #produce the answer and come back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)

    def test2_from_food_assertion_with_all_data(self):
        print("answer_question: Food Assertion with All Data")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"I've eat for lunch a pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #given the presence of all the data, the system registers the meal in the food diary and comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the recipe are produced
        self.assertTrue(response.info.strip() == '')
        #answer produced
        self.assertTrue(len(response.answer) > 0) 

    #run after all the tests
    def tearDown(self):
        uhp.delete_user_history("0")
        print("Test completed")


#OPENAI OK
#ANTHROPIC OK
class Test7ControllerProfileRecapAndUpdate(unittest.TestCase):
#PROFILE RECAP
    def test1_profile_recap_with_update(self):
        print("answer_question: Profile Recap")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the system moves to the profile recap state
        self.assertEqual(response.action, con.TASK_4_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the user data recap is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Yes please.",con.TASK_4_10_HOOK,None,response.info)
        print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_4_30_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"My surname is Bianchi",con.TASK_4_30_HOOK,None,response.info)
        print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)
        #the user data are updated
        self.assertEqual(userData.surname, "Bianchi")

    def test2_profile_recap_with_update2(self):
        print("answer_question: Profile Recap 2")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the system moves to the profile recap state
        self.assertEqual(response.action, con.TASK_4_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the user data recap is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Yes please.",con.TASK_4_10_HOOK,None,response.info)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_4_30_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)

        response = cc.answer_router(userData,"I'm allergic to fish, My surname is ",con.TASK_4_30_HOOK,None,response.info)
        print_answers(response)
        self.assertEqual(response.action, con.TASK_4_30_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)


        response = cc.answer_router(userData,"I'm allergic to fish, My surname is Neri",con.TASK_4_30_HOOK,None,response.info)
        print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced
        self.assertTrue(len(response.answer) > 0)
        #the user data are updated
        self.assertEqual(userData.surname, "Neri")

    def test3_profile_recap_with_no_update(self):
        print("answer_question: Profile Recap with No Update")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the system moves to the profile recap state
        self.assertEqual(response.action, con.TASK_4_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the user data recap is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"No thanks.",con.TASK_4_10_HOOK,None,response.info)
        print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced (beccause goes back to the hub)
        self.assertTrue(len(response.answer) > 0)

    def test4_profile_recap_with_no_update2(self):
        print("answer_question: Profile Recap with No Update 2, Unrelated Question")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What do you know about me?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the system moves to the profile recap state
        self.assertEqual(response.action, con.TASK_4_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the user data recap is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"What is the capital of Italy?",con.TASK_4_10_HOOK,None,response.info)
        print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the user are produced
        self.assertTrue(response.info.strip() == '')
        #answer is produced (beccause goes back to the hub)
        self.assertTrue(len(response.answer) > 0)
    
    def tearDown(self):
        up.delete_user_by_user_id("0")
        print("Test completed")

#OPENAI OK

class Test8ControllerFoodHistory(unittest.TestCase):
#FOOD HISTORY
    def test1_food_history_with_empty_history(self):
        print("answer_question: Food History with Empty History")
        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What is my food history?",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #the system moves to the food history state
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

    def test2_food_history_with_provided_history(self):
        print("answer_question: Food History with Provided History")

        userData = get_valid_user_data()
        response = cc.answer_router(userData,"I've eat for lunch a pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #given the presence of all the data, the system registers the meal in the food diary and comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the recipe are produced
        self.assertTrue(response.info.strip() == '')
        #answer produced
        self.assertTrue(len(response.answer) > 0)    

        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What is my food history?",con.TASK_1_HOOK,response.memory,"")  
        print_answers(response)
        #the system moves to the food history state
        self.assertEqual(response.action, con.TASK_5_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the recap of the food history is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Can you provide the sustainability of each ingredient involved?",con.TASK_5_10_HOOK,response.memory,"")  
        print_answers(response)
        #the system loop back to the food history state
        self.assertEqual(response.action, con.TASK_5_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Ok thanks!",con.TASK_5_10_HOOK,response.memory,"")  
        print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

    def test3_food_history_with_provided_history_and_change_topic(self):
        print("answer_question: Food History with Provided History and Change Topic")

        userData = get_valid_user_data()
        response = cc.answer_router(userData,"I've eat for lunch a pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #given the presence of all the data, the system registers the meal in the food diary and comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the recipe are produced
        self.assertTrue(response.info.strip() == '')
        #answer produced
        self.assertTrue(len(response.answer) > 0)    

        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What is my food history?",con.TASK_1_HOOK,response.memory,"")  
        print_answers(response)
        #the system moves to the food history state
        self.assertEqual(response.action, con.TASK_5_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the recap of the food history is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"And is mayonaise sustainable?",con.TASK_5_10_HOOK,response.memory,"")  
        print_answers(response)
        #the system goes to expert loop
        self.assertEqual(response.action, con.TASK_6_40_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"Ok thanks!",con.TASK_6_40_HOOK,response.memory,"")  
        print_answers(response)
        #the system comes back to the hub
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

    def test4_food_history_with_provided_history_and_change_unrelated_topic(self):
        print("answer_question: Food History with Provided History and Change Unrelated Topic")

        userData = get_valid_user_data()
        response = cc.answer_router(userData,"I've eat for lunch a pizza made of pizza dough, tomato, mozzarella and basil.",con.TASK_1_HOOK,None,"")
        print_answers(response)
        #given the presence of all the data, the system registers the meal in the food diary and comes back to the hub
        self.assertEqual(response.action, con.TASK_1_HOOK)
        #no info data of the recipe are produced
        self.assertTrue(response.info.strip() == '')
        #answer produced
        self.assertTrue(len(response.answer) > 0)    

        userData = get_valid_user_data()
        response = cc.answer_router(userData,"What is my food history?",con.TASK_1_HOOK,response.memory,"")  
        print_answers(response)
        #the system moves to the food history state
        self.assertEqual(response.action, con.TASK_5_10_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer with the recap of the food history is provided
        self.assertTrue(len(response.answer) != 0)

        response = cc.answer_router(userData,"What time is it?",con.TASK_5_10_HOOK,response.memory,"")  
        print_answers(response)
        #the system goes to hub
        self.assertEqual(response.action, con.TASK_MINUS_1_HOOK)
        #no info data are produced
        self.assertTrue(response.info.strip() == '')
        #the answer is provided
        self.assertTrue(len(response.answer) != 0)

#Utility functions
def get_user_data():
    return ud.User("Test", 0, None, None, None, None, None, None, None, None, None)

def get_valid_user_data():
    return ud.User("Test", 0, "Giacomo", "Rossi", "01/01/1990", "Italy", [], [], False, "", [])

def get_valid_user_data_with_impossible_constraints():
    return ud.User("Test", 0, "Giacomo", "Rossi", "01/01/1990", "Italy", [], ["halal"], False, "", [])

def print_answers(response, print_info = True):
    if print_info:
        print(response.answer)

if __name__ == '__main__':
    unittest.main()