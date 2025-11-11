import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock, call
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from collections import Counter

from src.logic import get_cache_response
from src.logic import history_serializer
from src.logic import get_chat_response
from src.logic import utterance_paraphraser
from src.logic import retrieve_context_with_metadata
from src.logic import is_somewhat_uniform
from src.logic import prepare_final_context
from src.logic import hash_string
from src.logic import _handle_single_module_case
from src.logic import _get_chitchat_cache_key
from src.logic import _handle_clear_preference_case
from src.logic import get_route_for_utterance
from src.logic import _determine_final_route
from src.logic import chat_responder_
from src.prompts import (
    # RAG_CONCISE_SYSTEM_PROMPT,
    # RAG_EXPLANATORY_SYSTEM_PROMPT,
    # RAG_NORMAL_SYSTEM_PROMPT,
    UTTERANCE_PARAPHRASER_PROMPT,
    # SQL_CONVERTER_MODIFIED_WITH_PARAMETERS,
    # CHITCHAT_PROMPT,
    # SQL_CONVERTER_MODIFIED_WITH_PARAMETERS_TEMPLATE,
    # SQL_MODIFIER,
    # ANSWER_VALIDATOR_PROMPT,
    SEMANTIC_ROUTER
    # SQL_CONVERTER,
)

OSS_LLM_MODEL_NAME = os.getenv("OSS_LLM_MODEL_NAME", "/gpt-120")
GPT_LLM_MODEL_NAME = os.getenv("GPT_LLM_MODEL_NAME", "/gpt-120")
OSS_API_KEY = os.getenv("OSS_API_KEY", "EMPTY")
GPT_API_KEY = os.getenv("GPT_API_KEY", "EMPTY")
OSS_API_BASE = os.getenv("OSS_API_BASE", "http://gpt-oss-120b-predictor.admin.svc.cluster.local/v1")
GPT_API_BASE = os.getenv("GPT_API_BASE", "http://gpt-oss-120b-predictor.admin.svc.cluster.local/v1")


# --- Test Cases ---

@pytest.mark.asyncio
@patch.dict("src.logic.config", {"cache": {"alpha_threshold": 0.1}})
@patch("src.logic.Cache")
async def test_get_cache_response_success(mock_cache_class):
    """
    Tests the "happy path" where a matching record with thumb_up > 0 is found.
    """
    # 1. Arrange
    mock_query = "سلام"
    expected_response = 'سلام. من دستیار دیجیتال نسل 4 هستم. می\u200cتوانم در مورد ماژول\u200cهای دفتر کل، انبار، فروش، گزارش ساز و خزانه داری به شما کمک کنم. پرسش خود را بپرسید تا در صورت امکان، پاسخ آن را ارائه دهم.'
    expected_url = ''
    
    mock_records = [
        {"response": expected_response, "url": expected_url, "thumb_up": 1}
    ]

    mock_cache_instance = MagicMock()
    mock_cache_instance.get_embedding_match = AsyncMock(return_value=mock_records)
    mock_cache_class.return_value = mock_cache_instance

    # 2. Act
    response, url = await get_cache_response(query=mock_query)

    # 3. Assert
    assert response == expected_response
    assert url == expected_url

    mock_cache_instance.get_embedding_match.assert_called_once_with(
        query=mock_query,
        threshold=0.1,
        knn=1
    )


@pytest.mark.asyncio
@patch.dict("src.logic.config", {"cache": {"alpha_threshold": 0.1}})
@patch("src.logic.Cache")
async def test_get_cache_response_no_match(mock_cache_class):
    """
    Tests the case where no matching records are found (returns an empty list).
    """
    mock_query = 'درباره همکاران سیستم بهم بگو'

    mock_cache_instance = MagicMock()
    mock_cache_instance.get_embedding_match = AsyncMock(return_value=[])
    mock_cache_class.return_value = mock_cache_instance

    response, url = await get_cache_response(query=mock_query)

    assert response == ""
    assert url == ""
    mock_cache_instance.get_embedding_match.assert_called_once()


@pytest.mark.asyncio
@patch.dict("src.logic.config", {"cache": {"alpha_threshold": 0.1}})
@patch("src.logic.Cache")
async def test_get_cache_response_match_with_thumb_down(mock_cache_class):
    """
    Tests the case where a record is found, but its 'thumb_up' is 0.
    """
    
    mock_query = "دمت گرم"

    mock_records = [
        {"response": '', "url": "", "thumb_up": 0}
    ]

    mock_cache_instance = MagicMock()
    mock_cache_instance.get_embedding_match = AsyncMock(return_value=mock_records)
    mock_cache_class.return_value = mock_cache_instance

    response, url = await get_cache_response(query=mock_query)

    assert response == ""
    assert url == ""
    mock_cache_instance.get_embedding_match.assert_called_once()


@pytest.mark.asyncio
@patch.dict("src.logic.config", {"cache": {"alpha_threshold": 0.01}})
@patch("src.logic.Cache")
async def test_get_cache_response_custom_threshold(mock_cache_class):
    """
    Tests that passing a 'threshold' argument overrides the config default.
    """
    mock_query = "دمت گرمی"
    custom_threshold = 0.01

    mock_cache_instance = MagicMock()
    mock_cache_instance.get_embedding_match = AsyncMock(return_value=[])
    mock_cache_class.return_value = mock_cache_instance

    response, url = await get_cache_response(query=mock_query, threshold=custom_threshold)

    expected_response = ""
    expected_url = ""
    
    assert response == expected_response
    assert url == expected_url

    mock_cache_instance.get_embedding_match.assert_called_once_with(
        query=mock_query,
        threshold=custom_threshold,
        knn=1
    )

@pytest.mark.asyncio
@patch.dict("src.logic.config", {"cache": {"alpha_threshold": 0.1}})
@patch("src.logic.Cache")
async def test_get_cache_response_success_good_th(mock_cache_class):
    """
    Tests that passing a 'threshold' argument overrides the config default.
    """
    mock_query = 'دمت گرمی'
    custom_threshold = 0.1
    mock_records = [
        {"response": 'اگر سوال دیگری بود در خدمتم ', "url": '', "thumb_up": 1}
    ]
    mock_cache_instance = MagicMock()
    mock_cache_instance.get_embedding_match = AsyncMock(return_value=mock_records)
    mock_cache_class.return_value = mock_cache_instance

    response, url = await get_cache_response(query=mock_query, threshold=custom_threshold)

    expected_response = 'اگر سوال دیگری بود در خدمتم '
    expected_url = ''
    
    assert response == expected_response
    assert url == expected_url

    mock_cache_instance.get_embedding_match.assert_called_once_with(
        query=mock_query,
        threshold=custom_threshold,
        knn=1
    )
    
### test of history_serializer

def test_history_serializer_empty_list():
    """
    Tests the function with an empty history list.
    """
    # 1. Arrange
    test_history = []
    expected_output = ""

    # 2. Act
    result = history_serializer(test_history)

    # 3. Assert
    assert result == expected_output

def test_history_serializer_single_item():
    """
    Tests the function with a single item in the history list.
    (Note: Based on your second example, I inferred the input)
    """
    # 1. Arrange
    test_history = [('چطوری سند انبار بزنم؟', None)]
    expected_output = 'USER: چطوری سند انبار بزنم؟\nASSISTANT: None\n\n'

    # 2. Act
    result = history_serializer(test_history)

    # 3. Assert
    assert result == expected_output

def test_history_serializer_multiple_items():
    """
    Tests the function with multiple items in the history list.
    """
    # 1. Arrange
    test_history = [
        ('چطوری سند انبار بزنم؟', None),
        ('همکاران', None),
        ('همکاران', None)
    ]
    expected_output = (
        'USER: چطوری سند انبار بزنم؟\nASSISTANT: None\n\n'
        'USER: همکاران\nASSISTANT: None\n\n'
        'USER: همکاران\nASSISTANT: None\n\n'
    )

    # 2. Act
    result = history_serializer(test_history)

    # 3. Assert
    assert result == expected_output

### test of get_chat_response

@pytest.mark.asyncio
@patch("src.logic.ChatOpenAI") # Patch where ChatOpenAI is USED
async def test_get_chat_response_success_standard_model(mock_chat_openai_class):
    """
    Tests the "happy path" with a standard model name.
    Verifies that 'extra_body' is an empty dict {}.
    """
    # 1. Arrange
    mock_prompt = """
    
Your task is to determine if the user's Farsi follow-up question is self-sufficient for a search or if it needs clarification to become an effective search query.
- If the user's follow-up question is already a standalone, complete, and clear query that contains all necessary information for search by itself, provide the original question directly without modification.
- If the question is ambiguous, incomplete, lacks necessary context (thus not maintaining the needed information by itself and needing clarification), or requires context from conversation history to be understood, paraphrase it into a clear, complete, and effective search query.

The primary goal is to output a query that faithfully represents the user's intent and is effective for search. Avoid rephrasing solely for brevity if the original question is already clear, complete, and self-contained. Preserve the *authenticity of user intent.*

**Important Guidelines:**

- **Do Not Provide Answers or Explanations:** Do not provide any answers, explanations, interpretations, commentary, or additional information. Your sole task is to provide the Farsi search query (either the original or a paraphrase if clarification was needed).
- **Understand User Intent:** Focus on capturing the underlying intent of the user's question.
- **Use Conversation History Appropriately (When Paraphrasing for Clarification):** If paraphrasing is necessary due to ambiguity or incompleteness, use the conversation history only to add the required context or clarification. Do not introduce information from previous modules if they are not relevant to the current question's clarification.
- **Handle Multi-Turn Context Completion:** When the user provides incomplete information in multiple turns (e.g., first asking an incomplete question, then providing missing context in a follow-up), combine the information from both turns to create a complete, coherent search query.
- **Preserve Original Wording (When Paraphrasing):** When paraphrasing is necessary, preserve the user's original wording as much as possible, especially key terms, as they are important for accurate search results. Only alter wording if essential for clarity or to resolve ambiguity.
- **Include All Key Aspects of the Question:** Ensure that all important aspects, details, and specific requirements of the user's question are present in the final query.
- **Do Not Mix Modules:** If the user switches from one module to another, focus solely on the current module.
- **Maintain Clarity and Completeness (When Paraphrasing):** If paraphrasing, ensure the resulting query is clear, complete, and has all necessary information, incorporating context from history if needed.
- **Context Integration for Incomplete Queries:** When a user's follow-up provides missing context (like module specification, location, or other clarifying details) for a previous incomplete question, integrate this context with the original question to form a complete search query.
- **Avoid Overgeneralization and Omission of Key Details (When Paraphrasing):** Ensure all essential details are preserved.
- **Paying Attention to the Importance of Words (When Paraphrasing):** If paraphrasing for clarification, use the user's specific words rather than synonyms, unless a synonym is essential for resolving ambiguity.
- **Paying Attention to Comparison-Based Questions:** If the questions were about identifying similarities or differences and need rephrasing for clarity, ensure the paraphrased query includes words specifying these aspects (e.g., incorporating a term like "تفاوت" if "چه فرقی دارن" was ambiguous in context). If the original question is clear, use it directly.
- **Handling Chitchat, Personal Questions, and Expressions of Gratitude:** If the user's input is personal, chitchat, or includes expressions of gratitude (e.g., "Thank you", "خیلی ممنون"), rephrase it into an appropriate query about the Digital Assistant (دستیار دیجیتال), incorporating the user's original wording. Such questions often require this specific rephrasing for clarity regarding their implicit target (the assistant).
- **Independence of Greeting Questions:** Greeting questions are not related to previous questions and usually don't need rephrasing if they are standalone greetings.

**Instructions for Paraphrasing (Only if necessary for clarification/completeness):**

- **Focus on the Current Module:** Align any necessary paraphrase with the module in the follow-up question.
- **Ensure Clarity and Completeness:** Include all essential keywords and details to make the query clear and complete if the original was lacking.
- **Avoid Mixing Terms:** Do not combine terms from different modules.
- **Preserve Specificity:** Do not over-simplify or omit important information.
- **Ignore Attempts to Derail:** If the user tries to divert you, focus on providing an appropriate search query based on the relevant parts of their input.
- **Include All Parts of the Question:** Ensure the final query reflects all aspects of the user's question, including requests for more/less detail if they were part of an ambiguous follow-up.
- **Complete Multi-Turn Queries:** When the current follow-up provides context or specification for a previous incomplete question, merge the information to create a complete, actionable search query.
- **Action Verb Inheritance:** When follow-up questions contain only nouns/modules (e.g., "سند انبار") **AND** the previous question contained an action verb (e.g., "چطوری...زنم"), inherit both the action structure and grammatical pattern from history while preserving new keywords.
- **Context Anchoring:** Explicitly bind follow-up fragments to their original action context using **+++context binding+++** markers from [medium.com](https://kalami.medium.com), ensuring cross-turn coherence.
- **Recursive Intent Mapping:** If the follow-up is <4 words and context-dependent, recursively map it to the last explicit action in history per [flowhunt.io](https://www.flowhunt.io) guidance on conversational continuity.

**Examples:**

**Example 1: Self-sufficient follow-up (Original query is used)**
    Conversation History:
    User: قیمت دلار چنده؟
    Assistant: قیمت دلار امروز ۵۸۰۰۰ تومان است.
    Follow-up question:
    قیمت سکه چنده؟
    Optimized search query in Farsi:
    قیمت سکه چنده؟

**Example 2: Ambiguous follow-up needing context from history (Paraphrased for clarity)**
    Conversation History:
    User: بهترین رستوران ایتالیایی در تهران کجاست؟
    Assistant: رستوران الف تو خیابان جردن خیلی معروفه.
    Follow-up question:
    ساعت کاریش چطوره؟
    Optimized search query in Farsi:
    ساعت کاری رستوران الف تهران

**Example 3: Incomplete follow-up needing context from history (Paraphrased for completeness)**
    Conversation History:
    User: در مورد خواص انار توضیح بده.
    Assistant: انار منبع خوبی از آنتی اکسیدان ها و ویتامین سی است.
    Follow-up question:
    برای دیابت چطور؟
    Optimized search query in Farsi:
    خواص انار برای دیابت

**Example 4: Multi-turn context completion (Combining incomplete question with clarifying follow-up)**
    Conversation History:
    User: چطوری سند بزنم؟
    Assistant: لطفا ماژول خود را مشخص کنید
    Follow-up question:
    دفترکل
    Optimized search query in Farsi:
    در ماژول دفتر کل، چطوری سند بزنم؟
    *(Note: The module name should always be placed in the very first part of the search query, containing (در ماژول), and followed by a comma.)*

**Example 5: Multi-turn context completion with location specification**
    Conversation History:
    User: بهترین رستوران کجاست؟
    Assistant: لطفا شهر مورد نظر خود را مشخص کنید
    Follow-up question:
    اصفهان
    Optimized search query in Farsi:
    بهترین رستوران اصفهان کجاست

**Example 6: Multi-turn context completion with category specification**
    Conversation History:
    User: قیمت گوشی چنده؟
    Assistant: لطفا مدل گوشی مورد نظر خود را مشخص کنید
    Follow-up question:
    آیفون ۱۵
    Optimized search query in Farsi:
    قیمت گوشی آیفون ۱۵ چنده

**Example 7: Chitchat / Expression of gratitude (Rephrased to be about the Digital Assistant)**
    Conversation History:
    User: یک شعر از حافظ بخون.
    Assistant: (یک غزل از حافظ می خواند)
    Follow-up question:
    عالی بود، خیلی ممنون!
    Optimized search query in Farsi:
    دستیار دیجیتال عالی بود خیلی ممنون

**Example 8: Ambiguous comparison question needing context and rephrasing**
    Conversation History:
    User: مشخصات گوشی سامسونگ گلکسی اس ۲۴ اولترا رو بگو.
    Assistant: این گوشی دارای دوربین ۲۰۰ مگاپیکسلی و پردازنده اسنپدراگون ۸ نسل ۳ است.
    User: مشخصات آیفون ۱۵ پرومکس چیه؟
    Assistant: آیفون ۱۵ پرومکس دوربین ۴۸ مگاپیکسلی و چیپست ای ۱۷ پرو دارد.
    Follow-up question:
    این دو تا چه فرقی با هم دارن؟
    Optimized search query in Farsi:
    تفاوت گوشی سامسونگ گلکسی اس ۲۴ اولترا و آیفون ۱۵ پرومکس

**Example 9: Self-sufficient comparison question (Original query is used)**
    Conversation History:
    User: قیمت پژو ۲۰۶ تیپ ۲ کارکرده مدل ۹۸ چنده؟
    Assistant: حدود ۳۵۰ میلیون تومان.
    Follow-up question:
    مقایسه قیمت پژو ۲۰۶ تیپ ۲ با تیپ ۵ مدل ۹۸
    Optimized search query in Farsi:
    مقایسه قیمت پژو ۲۰۶ تیپ ۲ با تیپ ۵ مدل ۹۸

**Example 10: Standalone greeting (Original query is used)**
    Conversation History:
    User: ساعت چنده؟
    Assistant: ساعت ۴:۱۵ بعد از ظهر.
    Follow-up question:
    سلام، خوبی؟
    Optimized search query in Farsi:
    سلام، خوبی؟

**Example 11: Multi-turn with service type specification**
    Conversation History:
    User: چطوری رزرو کنم؟
    Assistant: لطفا نوع سرویس مورد نظر خود را مشخص کنید
    Follow-up question:
    هتل
    Optimized search query in Farsi:
    چطوری هتل رزرو کنم

**Example 12: Avoiding restricted keywords (e.g., حسابداری) unless explicitly needed for clarification from user's follow-up**
    Conversation History:
    User: چطوری انبار تعریف کنم
    Assistant: برای تعریف انبار میتوانید از ماژول لجستیک استفاده کنید
    Follow-up question:
    ویژگی پیگیری چیه
    Optimized search query in Farsi:
    ویژگی پیگیری چیه
    *(Note: "انبار" is not added as "ویژگی پیگیری" is specific enough)*

**Example 13: Ambiguous follow-up requesting more detail, needing history**
    Conversation History:
    User: درباره تاریخچه پیدایش اینترنت توضیح بده.
    Assistant: اینترنت از پروژه آرپانت وزارت دفاع آمریکا شروع شد.
    Follow-up question:
    خیلی خلاصه گفتی، جزئیات بیشتری می خوام.
    Optimized search query in Farsi:
    جزئیات بیشتر درباره تاریخچه پیدایش اینترنت

**Example 14: User asks for assistant's "opinion" (Rephrased as a query about the assistant)**
    Conversation History:
    User: به نظرت بهترین فیلم ایرانی تاریخ سینما کدومه؟
    Assistant: انتخاب بهترین فیلم بستگی به سلیقه دارد، اما فیلم های زیادی مورد تحسین قرار گرفته اند.
    Follow-up question:
    نظر شخصی خودت چیه؟
    Optimized search query in Farsi:
    نظر شخصی دستیار دیجیتال درباره بهترین فیلم ایرانی تاریخ سینما

**Example 15: Follow-up switches context/module (Focus on current query)**
    Conversation History:
    User (Weather Module): هوای شیراز فردا چطوره؟
    Assistant: فردا شیراز نیمه ابری با احتمال بارش پراکنده است.
    Follow-up question:
    (Recipe Module) طرز تهیه کیک شکلاتی ساده رو بگو.
    Optimized search query in Farsi:
    طرز تهیه کیک شکلاتی ساده

**Example 16: Preserving user's specific terms when paraphrasing for clarification**
    Conversation History:
    User: جدیدترین گوشی های سامسونگ با قیمت مناسب کدامند؟
    Assistant: مدل های سری A سامسونگ معمولا قیمت مناسبی دارند، مانند گلکسی A55.
    Follow-up question:
    بین اینا، خوش دست ترینش برای من که دست کوچکی دارم کدومه؟
    Optimized search query in Farsi:
    خوش دست ترین گوشی جدید سامسونگ با قیمت مناسب برای دست کوچک
    *(Note: "خوش دست ترین" from user is preserved. "گوشی جدید سامسونگ با قیمت مناسب" is from context.)*

**Example 17: Follow-up that is already specific and complete**
    Conversation History:
    User: خلاصه کتاب "کیمیاگر" اثر پائولو کوئیلو رو میخواستم.
    Assistant: (خلاصه ای از کتاب ارائه می دهد)
    Follow-up question:
    تحلیل شخصیت سانتیاگو در کتاب کیمیاگر
    Optimized search query in Farsi:
    تحلیل شخصیت سانتیاگو در کتاب کیمیاگر

**New Example 18: Action inheritance from history**
    Conversation History:
    User: چطوری سند حسابداریزنم؟
    Assistant: لطفا نوع سند را مشخص کنید
    Follow-up question:
    سند انبار
    Optimized search query:
    چطوری سند انبار بزنم

**New Example 19: Cross-module action preservation**
    Conversation History: 
    User: نحوه ثبت سفارش فروش چگونه است؟
    Assistant: لطفا نوع کالا را مشخص نمایید
    Follow-up question:
    کالای دیجیتال
    Optimized search query:
    نحوه ثبت سفارش فروش کالای دیجیتال

**Conversation History:**



**Follow-up question:**
چطوری سند ابنار بزنم؟

**NOTE:**

- You should *NEVER EVER* add حسابداری , انبار , دفتر کل to the search query unless they explicitly involved in the Follow-up question and are needed for clarification.
- It is essential to eliminate any words that may be considered offensive in any language, ensuring inclusive and respectful communication.
- **Provide *Only* the search query in Farsi:** Do not add additional text or reasoning.
- Avoid adding "چیست" as a verb at the end of search queries if the original question didn't use it and is clear without it.
- History keywords should only be added to the query if the current question is a follow-up that is ambiguous or incomplete on its own and needs context from history for clarification.
- **Multi-Turn Context Integration:** When the user provides clarifying information (module, location, category, etc.) in response to an assistant's request for specification, combine this information with the previous incomplete question to create a complete search query.

**Optimized search query in Farsi:**
    """
    expected_response_content = 'چطوری سند انبار بزنم؟'
    
    mock_api_base = 'https://api.openai.com/v1'
    mock_api_key = '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'
    mock_model_name = "gpt-4.1-2025-04-14"

    # Mock the response object that ainvoke will return
    mock_llm_response = MagicMock()
    mock_llm_response.content = expected_response_content

    # Mock the instance of ChatOpenAI
    mock_llm_instance = MagicMock()
    mock_llm_instance.ainvoke = AsyncMock(return_value=mock_llm_response)
    
    # Make the patched ChatOpenAI class return our mock instance
    mock_chat_openai_class.return_value = mock_llm_instance

    extra = {
            }
    model_kwargs={}

    # 2. Act
    response = await get_chat_response(
        prompt=mock_prompt,
        model_name=mock_model_name,
        api_key=mock_api_key,
        api_base=mock_api_base
    )

    # 3. Assert
    assert response == expected_response_content

    # Assert ChatOpenAI was instantiated correctly
    mock_chat_openai_class.assert_called_once_with(
        openai_api_base=mock_api_base,
        model_name=mock_model_name,
        openai_api_key=mock_api_key,
        temperature=0,
        model_kwargs=model_kwargs,  # Was hardcoded to {} in the function
        extra_body=extra     # This is the key check for this test
    )

    # Assert ainvoke was called correctly
    mock_llm_instance.ainvoke.assert_called_once_with(
        [SystemMessage(content=mock_prompt)]
    )

@pytest.mark.asyncio
@patch("src.logic.ChatOpenAI") # Patch where ChatOpenAI is USED
async def test_get_chat_response_success_special_model(mock_chat_openai_class):
    """
    Tests the "happy path" with the special '/gpt-120' model.
    Verifies that 'extra_body' is populated correctly.
    """
    # 1. Arrange
    mock_prompt = """
    
Your task is to determine if the user's Farsi follow-up question is self-sufficient for a search or if it needs clarification to become an effective search query.
- If the user's follow-up question is already a standalone, complete, and clear query that contains all necessary information for search by itself, provide the original question directly without modification.
- If the question is ambiguous, incomplete, lacks necessary context (thus not maintaining the needed information by itself and needing clarification), or requires context from conversation history to be understood, paraphrase it into a clear, complete, and effective search query.

The primary goal is to output a query that faithfully represents the user's intent and is effective for search. Avoid rephrasing solely for brevity if the original question is already clear, complete, and self-contained. Preserve the *authenticity of user intent.*

**Important Guidelines:**

- **Do Not Provide Answers or Explanations:** Do not provide any answers, explanations, interpretations, commentary, or additional information. Your sole task is to provide the Farsi search query (either the original or a paraphrase if clarification was needed).
- **Understand User Intent:** Focus on capturing the underlying intent of the user's question.
- **Use Conversation History Appropriately (When Paraphrasing for Clarification):** If paraphrasing is necessary due to ambiguity or incompleteness, use the conversation history only to add the required context or clarification. Do not introduce information from previous modules if they are not relevant to the current question's clarification.
- **Handle Multi-Turn Context Completion:** When the user provides incomplete information in multiple turns (e.g., first asking an incomplete question, then providing missing context in a follow-up), combine the information from both turns to create a complete, coherent search query.
- **Preserve Original Wording (When Paraphrasing):** When paraphrasing is necessary, preserve the user's original wording as much as possible, especially key terms, as they are important for accurate search results. Only alter wording if essential for clarity or to resolve ambiguity.
- **Include All Key Aspects of the Question:** Ensure that all important aspects, details, and specific requirements of the user's question are present in the final query.
- **Do Not Mix Modules:** If the user switches from one module to another, focus solely on the current module.
- **Maintain Clarity and Completeness (When Paraphrasing):** If paraphrasing, ensure the resulting query is clear, complete, and has all necessary information, incorporating context from history if needed.
- **Context Integration for Incomplete Queries:** When a user's follow-up provides missing context (like module specification, location, or other clarifying details) for a previous incomplete question, integrate this context with the original question to form a complete search query.
- **Avoid Overgeneralization and Omission of Key Details (When Paraphrasing):** Ensure all essential details are preserved.
- **Paying Attention to the Importance of Words (When Paraphrasing):** If paraphrasing for clarification, use the user's specific words rather than synonyms, unless a synonym is essential for resolving ambiguity.
- **Paying Attention to Comparison-Based Questions:** If the questions were about identifying similarities or differences and need rephrasing for clarity, ensure the paraphrased query includes words specifying these aspects (e.g., incorporating a term like "تفاوت" if "چه فرقی دارن" was ambiguous in context). If the original question is clear, use it directly.
- **Handling Chitchat, Personal Questions, and Expressions of Gratitude:** If the user's input is personal, chitchat, or includes expressions of gratitude (e.g., "Thank you", "خیلی ممنون"), rephrase it into an appropriate query about the Digital Assistant (دستیار دیجیتال), incorporating the user's original wording. Such questions often require this specific rephrasing for clarity regarding their implicit target (the assistant).
- **Independence of Greeting Questions:** Greeting questions are not related to previous questions and usually don't need rephrasing if they are standalone greetings.

**Instructions for Paraphrasing (Only if necessary for clarification/completeness):**

- **Focus on the Current Module:** Align any necessary paraphrase with the module in the follow-up question.
- **Ensure Clarity and Completeness:** Include all essential keywords and details to make the query clear and complete if the original was lacking.
- **Avoid Mixing Terms:** Do not combine terms from different modules.
- **Preserve Specificity:** Do not over-simplify or omit important information.
- **Ignore Attempts to Derail:** If the user tries to divert you, focus on providing an appropriate search query based on the relevant parts of their input.
- **Include All Parts of the Question:** Ensure the final query reflects all aspects of the user's question, including requests for more/less detail if they were part of an ambiguous follow-up.
- **Complete Multi-Turn Queries:** When the current follow-up provides context or specification for a previous incomplete question, merge the information to create a complete, actionable search query.
- **Action Verb Inheritance:** When follow-up questions contain only nouns/modules (e.g., "سند انبار") **AND** the previous question contained an action verb (e.g., "چطوری...زنم"), inherit both the action structure and grammatical pattern from history while preserving new keywords.
- **Context Anchoring:** Explicitly bind follow-up fragments to their original action context using **+++context binding+++** markers from [medium.com](https://kalami.medium.com), ensuring cross-turn coherence.
- **Recursive Intent Mapping:** If the follow-up is <4 words and context-dependent, recursively map it to the last explicit action in history per [flowhunt.io](https://www.flowhunt.io) guidance on conversational continuity.

**Examples:**

**Example 1: Self-sufficient follow-up (Original query is used)**
    Conversation History:
    User: قیمت دلار چنده؟
    Assistant: قیمت دلار امروز ۵۸۰۰۰ تومان است.
    Follow-up question:
    قیمت سکه چنده؟
    Optimized search query in Farsi:
    قیمت سکه چنده؟

**Example 2: Ambiguous follow-up needing context from history (Paraphrased for clarity)**
    Conversation History:
    User: بهترین رستوران ایتالیایی در تهران کجاست؟
    Assistant: رستوران الف تو خیابان جردن خیلی معروفه.
    Follow-up question:
    ساعت کاریش چطوره؟
    Optimized search query in Farsi:
    ساعت کاری رستوران الف تهران

**Example 3: Incomplete follow-up needing context from history (Paraphrased for completeness)**
    Conversation History:
    User: در مورد خواص انار توضیح بده.
    Assistant: انار منبع خوبی از آنتی اکسیدان ها و ویتامین سی است.
    Follow-up question:
    برای دیابت چطور؟
    Optimized search query in Farsi:
    خواص انار برای دیابت

**Example 4: Multi-turn context completion (Combining incomplete question with clarifying follow-up)**
    Conversation History:
    User: چطوری سند بزنم؟
    Assistant: لطفا ماژول خود را مشخص کنید
    Follow-up question:
    دفترکل
    Optimized search query in Farsi:
    در ماژول دفتر کل، چطوری سند بزنم؟
    *(Note: The module name should always be placed in the very first part of the search query, containing (در ماژول), and followed by a comma.)*

**Example 5: Multi-turn context completion with location specification**
    Conversation History:
    User: بهترین رستوران کجاست؟
    Assistant: لطفا شهر مورد نظر خود را مشخص کنید
    Follow-up question:
    اصفهان
    Optimized search query in Farsi:
    بهترین رستوران اصفهان کجاست

**Example 6: Multi-turn context completion with category specification**
    Conversation History:
    User: قیمت گوشی چنده؟
    Assistant: لطفا مدل گوشی مورد نظر خود را مشخص کنید
    Follow-up question:
    آیفون ۱۵
    Optimized search query in Farsi:
    قیمت گوشی آیفون ۱۵ چنده

**Example 7: Chitchat / Expression of gratitude (Rephrased to be about the Digital Assistant)**
    Conversation History:
    User: یک شعر از حافظ بخون.
    Assistant: (یک غزل از حافظ می خواند)
    Follow-up question:
    عالی بود، خیلی ممنون!
    Optimized search query in Farsi:
    دستیار دیجیتال عالی بود خیلی ممنون

**Example 8: Ambiguous comparison question needing context and rephrasing**
    Conversation History:
    User: مشخصات گوشی سامسونگ گلکسی اس ۲۴ اولترا رو بگو.
    Assistant: این گوشی دارای دوربین ۲۰۰ مگاپیکسلی و پردازنده اسنپدراگون ۸ نسل ۳ است.
    User: مشخصات آیفون ۱۵ پرومکس چیه؟
    Assistant: آیفون ۱۵ پرومکس دوربین ۴۸ مگاپیکسلی و چیپست ای ۱۷ پرو دارد.
    Follow-up question:
    این دو تا چه فرقی با هم دارن؟
    Optimized search query in Farsi:
    تفاوت گوشی سامسونگ گلکسی اس ۲۴ اولترا و آیفون ۱۵ پرومکس

**Example 9: Self-sufficient comparison question (Original query is used)**
    Conversation History:
    User: قیمت پژو ۲۰۶ تیپ ۲ کارکرده مدل ۹۸ چنده؟
    Assistant: حدود ۳۵۰ میلیون تومان.
    Follow-up question:
    مقایسه قیمت پژو ۲۰۶ تیپ ۲ با تیپ ۵ مدل ۹۸
    Optimized search query in Farsi:
    مقایسه قیمت پژو ۲۰۶ تیپ ۲ با تیپ ۵ مدل ۹۸

**Example 10: Standalone greeting (Original query is used)**
    Conversation History:
    User: ساعت چنده؟
    Assistant: ساعت ۴:۱۵ بعد از ظهر.
    Follow-up question:
    سلام، خوبی؟
    Optimized search query in Farsi:
    سلام، خوبی؟

**Example 11: Multi-turn with service type specification**
    Conversation History:
    User: چطوری رزرو کنم؟
    Assistant: لطفا نوع سرویس مورد نظر خود را مشخص کنید
    Follow-up question:
    هتل
    Optimized search query in Farsi:
    چطوری هتل رزرو کنم

**Example 12: Avoiding restricted keywords (e.g., حسابداری) unless explicitly needed for clarification from user's follow-up**
    Conversation History:
    User: چطوری انبار تعریف کنم
    Assistant: برای تعریف انبار میتوانید از ماژول لجستیک استفاده کنید
    Follow-up question:
    ویژگی پیگیری چیه
    Optimized search query in Farsi:
    ویژگی پیگیری چیه
    *(Note: "انبار" is not added as "ویژگی پیگیری" is specific enough)*

**Example 13: Ambiguous follow-up requesting more detail, needing history**
    Conversation History:
    User: درباره تاریخچه پیدایش اینترنت توضیح بده.
    Assistant: اینترنت از پروژه آرپانت وزارت دفاع آمریکا شروع شد.
    Follow-up question:
    خیلی خلاصه گفتی، جزئیات بیشتری می خوام.
    Optimized search query in Farsi:
    جزئیات بیشتر درباره تاریخچه پیدایش اینترنت

**Example 14: User asks for assistant's "opinion" (Rephrased as a query about the assistant)**
    Conversation History:
    User: به نظرت بهترین فیلم ایرانی تاریخ سینما کدومه؟
    Assistant: انتخاب بهترین فیلم بستگی به سلیقه دارد، اما فیلم های زیادی مورد تحسین قرار گرفته اند.
    Follow-up question:
    نظر شخصی خودت چیه؟
    Optimized search query in Farsi:
    نظر شخصی دستیار دیجیتال درباره بهترین فیلم ایرانی تاریخ سینما

**Example 15: Follow-up switches context/module (Focus on current query)**
    Conversation History:
    User (Weather Module): هوای شیراز فردا چطوره؟
    Assistant: فردا شیراز نیمه ابری با احتمال بارش پراکنده است.
    Follow-up question:
    (Recipe Module) طرز تهیه کیک شکلاتی ساده رو بگو.
    Optimized search query in Farsi:
    طرز تهیه کیک شکلاتی ساده

**Example 16: Preserving user's specific terms when paraphrasing for clarification**
    Conversation History:
    User: جدیدترین گوشی های سامسونگ با قیمت مناسب کدامند؟
    Assistant: مدل های سری A سامسونگ معمولا قیمت مناسبی دارند، مانند گلکسی A55.
    Follow-up question:
    بین اینا، خوش دست ترینش برای من که دست کوچکی دارم کدومه؟
    Optimized search query in Farsi:
    خوش دست ترین گوشی جدید سامسونگ با قیمت مناسب برای دست کوچک
    *(Note: "خوش دست ترین" from user is preserved. "گوشی جدید سامسونگ با قیمت مناسب" is from context.)*

**Example 17: Follow-up that is already specific and complete**
    Conversation History:
    User: خلاصه کتاب "کیمیاگر" اثر پائولو کوئیلو رو میخواستم.
    Assistant: (خلاصه ای از کتاب ارائه می دهد)
    Follow-up question:
    تحلیل شخصیت سانتیاگو در کتاب کیمیاگر
    Optimized search query in Farsi:
    تحلیل شخصیت سانتیاگو در کتاب کیمیاگر

**New Example 18: Action inheritance from history**
    Conversation History:
    User: چطوری سند حسابداریزنم؟
    Assistant: لطفا نوع سند را مشخص کنید
    Follow-up question:
    سند انبار
    Optimized search query:
    چطوری سند انبار بزنم

**New Example 19: Cross-module action preservation**
    Conversation History: 
    User: نحوه ثبت سفارش فروش چگونه است؟
    Assistant: لطفا نوع کالا را مشخص نمایید
    Follow-up question:
    کالای دیجیتال
    Optimized search query:
    نحوه ثبت سفارش فروش کالای دیجیتال

**Conversation History:**



**Follow-up question:**
چطوری سند ابنار بزنم؟

**NOTE:**

- You should *NEVER EVER* add حسابداری , انبار , دفتر کل to the search query unless they explicitly involved in the Follow-up question and are needed for clarification.
- It is essential to eliminate any words that may be considered offensive in any language, ensuring inclusive and respectful communication.
- **Provide *Only* the search query in Farsi:** Do not add additional text or reasoning.
- Avoid adding "چیست" as a verb at the end of search queries if the original question didn't use it and is clear without it.
- History keywords should only be added to the query if the current question is a follow-up that is ambiguous or incomplete on its own and needs context from history for clarification.
- **Multi-Turn Context Integration:** When the user provides clarifying information (module, location, category, etc.) in response to an assistant's request for specification, combine this information with the previous incomplete question to create a complete search query.

**Optimized search query in Farsi:**
    """
    expected_response_content = "چطوری سند انبار بزنم؟"
    
    mock_api_base = 'http://gpt-oss-120b-predictor.admin.svc.cluster.local/v1'
    mock_api_key = 'EMPTY'
    mock_model_name = "/gpt-120"

    # Mock the response object that ainvoke will return
    mock_llm_response = MagicMock()
    mock_llm_response.content = expected_response_content

    # Mock the instance of ChatOpenAI
    mock_llm_instance = MagicMock()
    mock_llm_instance.ainvoke = AsyncMock(return_value=mock_llm_response)
    
    # Make the patched ChatOpenAI class return our mock instance
    mock_chat_openai_class.return_value = mock_llm_instance

    extra = {
                "top_k": 1,
                "do_sample": False,
                "seed": 42,
                "sampling_method": "greedy",
                "reasoning_effort": "medium"
            }
    model_kwargs={}

    # 2. Act
    response = await get_chat_response(
        prompt=mock_prompt,
        model_name=mock_model_name,
        api_key=mock_api_key,
        api_base=mock_api_base
    )

    # 3. Assert
    assert response == expected_response_content

    # Assert ChatOpenAI was instantiated correctly
    mock_chat_openai_class.assert_called_once_with(
        openai_api_base=mock_api_base,
        model_name=mock_model_name,
        openai_api_key=mock_api_key,
        temperature=0,
        model_kwargs=model_kwargs,  # Was hardcoded to {} in the function
        extra_body=extra     # This is the key check for this test
    )

    # Assert ainvoke was called correctly
    mock_llm_instance.ainvoke.assert_called_once_with(
        [SystemMessage(content=mock_prompt)]
    )

@pytest.mark.asyncio
async def test_get_chat_response_raises_value_error_on_missing_config():
    """
    Tests that a ValueError is raised if api_base is missing.
    No mocks are needed as it should fail before creating a class.
    """
    # 1. Arrange
    mock_prompt = "Test"
    
    # 2. Act & 3. Assert
    with pytest.raises(ValueError, match="No valid LLM configuration"):
        await get_chat_response(
            prompt=mock_prompt,
            api_base=None # Trigger the failure condition
        )

    with pytest.raises(ValueError, match="No valid LLM configuration"):
        await get_chat_response(
            prompt=mock_prompt,
            model_name=None # Trigger the other failure condition
        )


@pytest.mark.asyncio
# 2. Patch the dependencies, bottom-up
@patch("src.logic.json_cleaning_1")
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
@patch("src.logic.history_serializer")
async def test_utterance_paraphraser_with_assistant_name(
    mock_history_serializer, 
    mock_get_chat_response, 
    mock_json_cleaning_1
):
    """
    Tests the "happy path" when an 'assistant_name' IS provided.
    It should format the prompt using history, assistant_name, and question.
    """
    # 1. Arrange
    mock_history = [['نحوه صدور سند حسابداری برای رسید خرید داخلی ؟', 'برای صدور سند حسابداری از رسید خرید داخلی، مراحل زیر را دنبال کنید:\n\n1. در صفحهٔ رسید خرید داخلی، روی منوی سه نقطه (⋮) کلیک کنید.  \n2. گزینه **«صدور سند حسابداری»** را انتخاب کنید.  \n3. در فرم باز شده، تاریخ، شمارهٔ فرعی و شرح سند حسابداری را وارد کنید.  \n4. دکمه **«صدور سند حسابداری»** را فشار دهید.  \n\nدر صورت تنظیم صحیح استقرار حساب\u200cها، سند حسابداری با نوع «دریافت و پرداخت» در دفترکل ایجاد می\u200cشود.'], ['چطوری کد استاندارد به کالا بدم؟', 'برای اختصاص کد استاندارد به کالا، از **الگوی کدگذاری** استفاده می\u200cکنید:\n\n1. در ماژول لجستیک → اطلاعات پایه → «معرفی الگوی کدگذاری» یک الگوی جدید تعریف کنید (عنوان، فرایند\u202f=\u202fکد\u202fیا\u202fعنوان کالا، شرط تکرار و اقلام مورد نیاز مثل ویژگی، گروهبندی، مقدار ثابت یا شمارنده).  \n2. الگوی ایجاد شده باید **فعال** باشد.  \n3. هنگام تعریف یا ویرایش کالا، در فیلد **کد** یا **عنوان** روی گزینه کدگذاری کلیک کنید و الگوی فعال را انتخاب کنید.  \n4. مقادیر مورد نیاز الگو (مثلاً ویژگی\u200cهای کالا یا گروهبندی) را در فرم کالا تکمیل کنید؛ در غیر این صورت پیام خطا نمایش داده می\u200cشود.  \n5. سیستم بر پایه الگو، کد استاندارد را به\u200cصورت خودکار تولید و در فیلد مربوطه قرار می\u200cدهد.  \n\nبه این ترتیب کد کالا بر اساس الگوی تعریف\u200cشده استاندارد می\u200cشود.'], ['چطوری کد استاندارد به کالاهایم بدهم؟', None]]
    mock_utterance = 'چطوری کد استاندارد به کالاهایم بدهم؟'
    mock_assistant = "gpt"
    
    mock_serialized_history = 'USER: نحوه صدور سند حسابداری برای رسید خرید داخلی ؟\nASSISTANT: برای صدور سند حسابداری از رسید خرید داخلی، مراحل زیر را دنبال کنید:\n\n1. در صفحهٔ رسید خرید داخلی، روی منوی سه نقطه (⋮) کلیک کنید.  \n2. گزینه **«صدور سند حسابداری»** را انتخاب کنید.  \n3. در فرم باز شده، تاریخ، شمارهٔ فرعی و شرح سند حسابداری را وارد کنید.  \n4. دکمه **«صدور سند حسابداری»** را فشار دهید.  \n\nدر صورت تنظیم صحیح استقرار حساب\u200cها، سند حسابداری با نوع «دریافت و پرداخت» در دفترکل ایجاد می\u200cشود.\n\nUSER: چطوری کد استاندارد به کالا بدم؟\nASSISTANT: برای اختصاص کد استاندارد به کالا، از **الگوی کدگذاری** استفاده می\u200cکنید:\n\n1. در ماژول لجستیک → اطلاعات پایه → «معرفی الگوی کدگذاری» یک الگوی جدید تعریف کنید (عنوان، فرایند\u202f=\u202fکد\u202fیا\u202fعنوان کالا، شرط تکرار و اقلام مورد نیاز مثل ویژگی، گروهبندی، مقدار ثابت یا شمارنده).  \n2. الگوی ایجاد شده باید **فعال** باشد.  \n3. هنگام تعریف یا ویرایش کالا، در فیلد **کد** یا **عنوان** روی گزینه کدگذاری کلیک کنید و الگوی فعال را انتخاب کنید.  \n4. مقادیر مورد نیاز الگو (مثلاً ویژگی\u200cهای کالا یا گروهبندی) را در فرم کالا تکمیل کنید؛ در غیر این صورت پیام خطا نمایش داده می\u200cشود.  \n5. سیستم بر پایه الگو، کد استاندارد را به\u200cصورت خودکار تولید و در فیلد مربوطه قرار می\u200cدهد.  \n\nبه این ترتیب کد کالا بر اساس الگوی تعریف\u200cشده استاندارد می\u200cشود.\n\nUSER: چطوری کد استاندارد به کالاهایم بدهم؟\nASSISTANT: None\n\n'
    
    mock_llm_response = 'چطوری کد استاندارد به کالاهایم بدهم؟'
    expected_final_response = 'چطوری کد استاندارد به کالاهایم بدهم؟'

    # Configure the mocks
    mock_history_serializer.return_value = mock_serialized_history
    mock_get_chat_response.return_value = mock_llm_response
    mock_json_cleaning_1.return_value = expected_final_response

    # Calculate the exact prompt we expect to be generated
    expected_prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
        history=mock_serialized_history,
        assistant_name=mock_assistant,
        question=mock_utterance
    )

    # 2. Act
    result = await utterance_paraphraser(
        history=mock_history,
        user_utterance=mock_utterance,
        assistant_name=mock_assistant
    )

    # 3. Assert
    assert result == expected_final_response
    
    # Check that all dependencies were called correctly
    mock_history_serializer.assert_called_once_with(mock_history)
    mock_get_chat_response.assert_called_once_with(expected_prompt)
    mock_json_cleaning_1.assert_called_once_with(mock_llm_response)

@pytest.mark.asyncio
# 2. Patch the dependencies, bottom-up
@patch("src.logic.json_cleaning_1")
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
@patch("src.logic.history_serializer")
async def test_utterance_paraphraser_no_assistant_name(
    mock_history_serializer, 
    mock_get_chat_response, 
    mock_json_cleaning_1
):
    """
    Tests the "happy path" when an 'assistant_name' IS provided.
    It should format the prompt using history, assistant_name, and question.
    """
    # 1. Arrange
    mock_history = [['نحوه صدور سند حسابداری برای رسید خرید داخلی ؟', 'برای صدور سند حسابداری از رسید خرید داخلی، مراحل زیر را دنبال کنید:\n\n1. در صفحهٔ رسید خرید داخلی، روی منوی سه نقطه (⋮) کلیک کنید.  \n2. گزینه **«صدور سند حسابداری»** را انتخاب کنید.  \n3. در فرم باز شده، تاریخ، شمارهٔ فرعی و شرح سند حسابداری را وارد کنید.  \n4. دکمه **«صدور سند حسابداری»** را فشار دهید.  \n\nدر صورت تنظیم صحیح استقرار حساب\u200cها، سند حسابداری با نوع «دریافت و پرداخت» در دفترکل ایجاد می\u200cشود.'], ['چطوری کد استاندارد به کالا بدم؟', 'برای اختصاص کد استاندارد به کالا، از **الگوی کدگذاری** استفاده می\u200cکنید:\n\n1. در ماژول لجستیک → اطلاعات پایه → «معرفی الگوی کدگذاری» یک الگوی جدید تعریف کنید (عنوان، فرایند\u202f=\u202fکد\u202fیا\u202fعنوان کالا، شرط تکرار و اقلام مورد نیاز مثل ویژگی، گروهبندی، مقدار ثابت یا شمارنده).  \n2. الگوی ایجاد شده باید **فعال** باشد.  \n3. هنگام تعریف یا ویرایش کالا، در فیلد **کد** یا **عنوان** روی گزینه کدگذاری کلیک کنید و الگوی فعال را انتخاب کنید.  \n4. مقادیر مورد نیاز الگو (مثلاً ویژگی\u200cهای کالا یا گروهبندی) را در فرم کالا تکمیل کنید؛ در غیر این صورت پیام خطا نمایش داده می\u200cشود.  \n5. سیستم بر پایه الگو، کد استاندارد را به\u200cصورت خودکار تولید و در فیلد مربوطه قرار می\u200cدهد.  \n\nبه این ترتیب کد کالا بر اساس الگوی تعریف\u200cشده استاندارد می\u200cشود.'], ['چطوری کد استاندارد به کالاهایم بدهم؟', None]]
    mock_utterance = 'چطوری کد استاندارد به کالاهایم بدهم؟'
    mock_assistant = None
    
    mock_serialized_history = 'USER: نحوه صدور سند حسابداری برای رسید خرید داخلی ؟\nASSISTANT: برای صدور سند حسابداری از رسید خرید داخلی، مراحل زیر را دنبال کنید:\n\n1. در صفحهٔ رسید خرید داخلی، روی منوی سه نقطه (⋮) کلیک کنید.  \n2. گزینه **«صدور سند حسابداری»** را انتخاب کنید.  \n3. در فرم باز شده، تاریخ، شمارهٔ فرعی و شرح سند حسابداری را وارد کنید.  \n4. دکمه **«صدور سند حسابداری»** را فشار دهید.  \n\nدر صورت تنظیم صحیح استقرار حساب\u200cها، سند حسابداری با نوع «دریافت و پرداخت» در دفترکل ایجاد می\u200cشود.\n\nUSER: چطوری کد استاندارد به کالا بدم؟\nASSISTANT: برای اختصاص کد استاندارد به کالا، از **الگوی کدگذاری** استفاده می\u200cکنید:\n\n1. در ماژول لجستیک → اطلاعات پایه → «معرفی الگوی کدگذاری» یک الگوی جدید تعریف کنید (عنوان، فرایند\u202f=\u202fکد\u202fیا\u202fعنوان کالا، شرط تکرار و اقلام مورد نیاز مثل ویژگی، گروهبندی، مقدار ثابت یا شمارنده).  \n2. الگوی ایجاد شده باید **فعال** باشد.  \n3. هنگام تعریف یا ویرایش کالا، در فیلد **کد** یا **عنوان** روی گزینه کدگذاری کلیک کنید و الگوی فعال را انتخاب کنید.  \n4. مقادیر مورد نیاز الگو (مثلاً ویژگی\u200cهای کالا یا گروهبندی) را در فرم کالا تکمیل کنید؛ در غیر این صورت پیام خطا نمایش داده می\u200cشود.  \n5. سیستم بر پایه الگو، کد استاندارد را به\u200cصورت خودکار تولید و در فیلد مربوطه قرار می\u200cدهد.  \n\nبه این ترتیب کد کالا بر اساس الگوی تعریف\u200cشده استاندارد می\u200cشود.\n\nUSER: چطوری کد استاندارد به کالاهایم بدهم؟\nASSISTANT: None\n\n'
    
    mock_llm_response = 'چطوری کد استاندارد به کالاهایم بدهم؟'
    expected_final_response = 'چطوری کد استاندارد به کالاهایم بدهم؟'

    # Configure the mocks
    mock_history_serializer.return_value = mock_serialized_history
    mock_get_chat_response.return_value = mock_llm_response
    mock_json_cleaning_1.return_value = expected_final_response

    # Calculate the exact prompt we expect to be generated
    expected_prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
        history=mock_serialized_history,
        question=mock_utterance
    )

    # 2. Act
    result = await utterance_paraphraser(
        history=mock_history,
        user_utterance=mock_utterance,
        assistant_name=mock_assistant
    )

    # 3. Assert
    assert result == expected_final_response
    
    # Check that all dependencies were called correctly
    mock_history_serializer.assert_called_once_with(mock_history)
    mock_get_chat_response.assert_called_once_with(expected_prompt)
    mock_json_cleaning_1.assert_called_once_with(mock_llm_response)


@pytest.mark.asyncio
# 2. Patch the dependencies, bottom-up
@patch("src.logic.json_cleaning_1")
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
@patch("src.logic.history_serializer")
async def test_utterance_paraphraser_no_assistant_name_medium(
    mock_history_serializer, 
    mock_get_chat_response, 
    mock_json_cleaning_1
):
    """
    Tests the "happy path" when an 'assistant_name' IS provided.
    It should format the prompt using history, assistant_name, and question.
    """
    # 1. Arrange
    mock_history = [['روش ثبت خرید کالا در انبار به چه صورته؟', 'برای ثبت خرید کالا در انبار مراحل زیر را انجام دهید:\n\n1. از منوی **انبار → حسابداری انبار** گزینه **ثبت سند انبار (+)** را انتخاب کنید.  \n2. شرکت و الگوی سند مورد نظر را انتخاب کنید (در صورت نیاز می\u200cتوانید الگو را به منو اضافه کنید).  \n3. فیلدهای اجباری را تکمیل کنید:  \n   * **انبار** – انبار مربوط به شرکت، فعال و مطابق با الگوی انتخابی.  \n   * **طرف مقابل** – لیست طرف\u200cهای مقابل بر اساس الگوی سند فیلتر می\u200cشود.  \n   * **تاریخ** – تاریخ ثبت سند.  \n   * **شماره** – در صورت تعریف روش شماره\u200cگذاری، به\u200cصورت خودکار؛ در غیر این صورت به\u200cصورت دستی وارد می\u200cشود.  \n4. در بخش اقلام، کالاهای خریداری شده را انتخاب کنید، واحد سنجش و مقدار را وارد کنید.  \n5. در فیلد **فی قیمت** قیمت واحد را وارد کنید؛ سیستم مبلغ کل را بر اساس تعداد محاسبه می\u200cکند.  \n6. در صورت نیاز می\u200cتوانید **تخفیف، کرایه حمل** و سایر عوامل مبلغی را از طریق گزینه «عوامل مبلغی» تنظیم کنید.  \n7. برای محاسبه مالیات بر ارزش افزوده، پیش\u200cنیازهای تعریف گروه\u200cهای مالیاتی کالا و طرف تجاری باید موجود باشد.  \n8. پس از تکمیل تمام اطلاعات، سند را **ذخیره** کنید.  \n\nبه این ترتیب خرید کالا در انبار ثبت می\u200cشود.']]
    mock_utterance = 'بیشتر توضیح بده'
    mock_assistant = None
    
    mock_serialized_history = 'USER: روش ثبت خرید کالا در انبار به چه صورته؟\nASSISTANT: برای ثبت خرید کالا در انبار مراحل زیر را انجام دهید:\n\n1. از منوی **انبار → حسابداری انبار** گزینه **ثبت سند انبار (+)** را انتخاب کنید.  \n2. شرکت و الگوی سند مورد نظر را انتخاب کنید (در صورت نیاز می\u200cتوانید الگو را به منو اضافه کنید).  \n3. فیلدهای اجباری را تکمیل کنید:  \n   * **انبار** – انبار مربوط به شرکت، فعال و مطابق با الگوی انتخابی.  \n   * **طرف مقابل** – لیست طرف\u200cهای مقابل بر اساس الگوی سند فیلتر می\u200cشود.  \n   * **تاریخ** – تاریخ ثبت سند.  \n   * **شماره** – در صورت تعریف روش شماره\u200cگذاری، به\u200cصورت خودکار؛ در غیر این صورت به\u200cصورت دستی وارد می\u200cشود.  \n4. در بخش اقلام، کالاهای خریداری شده را انتخاب کنید، واحد سنجش و مقدار را وارد کنید.  \n5. در فیلد **فی قیمت** قیمت واحد را وارد کنید؛ سیستم مبلغ کل را بر اساس تعداد محاسبه می\u200cکند.  \n6. در صورت نیاز می\u200cتوانید **تخفیف، کرایه حمل** و سایر عوامل مبلغی را از طریق گزینه «عوامل مبلغی» تنظیم کنید.  \n7. برای محاسبه مالیات بر ارزش افزوده، پیش\u200cنیازهای تعریف گروه\u200cهای مالیاتی کالا و طرف تجاری باید موجود باشد.  \n8. پس از تکمیل تمام اطلاعات، سند را **ذخیره** کنید.  \n\nبه این ترتیب خرید کالا در انبار ثبت می\u200cشود.\n\n'
    
    mock_llm_response = 'توضیح بیشتر درباره روش ثبت خرید کالا در انبار'
    expected_final_response = 'توضیح بیشتر درباره روش ثبت خرید کالا در انبار'

    # Configure the mocks
    mock_history_serializer.return_value = mock_serialized_history
    mock_get_chat_response.return_value = mock_llm_response
    mock_json_cleaning_1.return_value = expected_final_response

    # Calculate the exact prompt we expect to be generated
    expected_prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
        history=mock_serialized_history,
        question=mock_utterance
    )

    # 2. Act
    result = await utterance_paraphraser(
        history=mock_history,
        user_utterance=mock_utterance,
        assistant_name=mock_assistant
    )

    # 3. Assert
    assert result == expected_final_response
    
    # Check that all dependencies were called correctly
    mock_history_serializer.assert_called_once_with(mock_history)
    mock_get_chat_response.assert_called_once_with(expected_prompt)
    mock_json_cleaning_1.assert_called_once_with(mock_llm_response)

@pytest.mark.asyncio
@patch("src.logic.json_cleaning_1")
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
@patch("src.logic.history_serializer")
async def test_utterance_paraphraser_empty_history(
    mock_history_serializer, 
    mock_get_chat_response, 
    mock_json_cleaning_1
):
    """
    Tests the "happy path" when an 'assistant_name' IS provided.
    It should format the prompt using history, assistant_name, and question.
    """
    # 1. Arrange
    mock_history = []
    mock_utterance = 'چطوری کد استاندارد به کالاهایم بدهم؟'
    mock_assistant = None
    
    mock_serialized_history = ""
    
    mock_llm_response = 'چطوری کد استاندارد به کالاهایم بدهم؟'
    expected_final_response = 'چطوری کد استاندارد به کالاهایم بدهم؟'

    # Configure the mocks
    mock_history_serializer.return_value = mock_serialized_history
    mock_get_chat_response.return_value = mock_llm_response
    mock_json_cleaning_1.return_value = expected_final_response

    # Calculate the exact prompt we expect to be generated
    expected_prompt = UTTERANCE_PARAPHRASER_PROMPT.format(
        history=mock_serialized_history,
        assistant_name=mock_assistant,
        question=mock_utterance
    )

    # 2. Act
    result = await utterance_paraphraser(
        history=mock_history,
        user_utterance=mock_utterance,
        assistant_name=mock_assistant
    )

    # 3. Assert
    assert result == expected_final_response
    
    # Check that all dependencies were called correctly
    mock_history_serializer.assert_called_once_with(mock_history)
    mock_get_chat_response.assert_called_once_with(expected_prompt)
    mock_json_cleaning_1.assert_called_once_with(mock_llm_response)

### test retrieve_context

@pytest.mark.asyncio
@patch("src.logic.Retriever") # Patch the Retriever class where it's USED
async def test_retrieve_context_with_input_modules(mock_retriever_class):
    """
    Tests the 'if input_modules:' branch.
    Ensures 'retrieve_context' is called with the 'module_filter' keyword argument.
    """
    # 1. Arrange
    mock_modules = ['دفتر کل']
    mock_query = 'در ماژول دفتر کل، چطوری سند تعریف کنم؟'
    mock_index = '../VectorDB'
    expected_context = [{"text": "# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه شرح های استاندارد\nشرح های استاندارد شرح هایی از سند هستند که اغلب تکرار می شوند و برای راحتی و تسریع انجام کار، تعریف می شوند.\nدر این بخش میتوانید با زدن کلید \" جدید\" چندین شرح استاندارد تعریف کنید.\nاین شرح ها در قلم سند حسابداری با انتخاب معین مربوطه به صورت سلکتور نمایش داده میشوند و شما میتوانید شرح دلخواه را انتخاب و در صورت نیاز تکمیل یا ویرایش کنید.\nشرح های استاندارد همواره قابل ویرایش هستند.\nپس از تکمیل اطلاعات، میتوانید حساب معین مورد نظر خود را ذخیره کنید.\n* امکان حذف یک حساب معین پس از استفاده وجود ندارد.\n* **راه اندازی اولیه:** با استفاده از این امکان از مسیر حسابداری مالی/ دفتر کل می‌توان در صورتیکه در سیستم ساختار حسابی تعریف نشده باشد، یک ساختار حساب ایجاد کرد.\nبرای اینکار در قسمت ساختار حساب‌ها و دفتر، گزینه ایجاد انتخاب می‌شود. یک ساختار حساب عمومی در سیستم ایجاد می‌گردد و با یک دفتری که ایجاد می‌شود، مرتبط می‌گردد. همچنین می‌توان با استفاده از گزینه دانلود، فایل ساختار حساب نمونه‌ای که ایجاد می‌شود را دانلود کرد و برای ایمپورت در سیستم استفاده کرد.\nنکته: راه اندازی اولیه به ازای هر شرکت انجام می شود.\n", "index": 12, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# تنظیمات دفتر کل\n## تنظیمات سند حسابداری\n### تنظیمات سایر ماژول ها\nبا فعال کردن این مورد، مجوز امکان ویرایش شماره فرعی و شرح سند در وضعیت بررسی به بعد برای اسناد صادر شده از دیگر ماژول ها وجود خواهد داشت.\nدر صورت انتخاب این بخش یک صفحه باز می‌شود که می‌توان به ازای هر دفتر، تیک فعال را انتخاب و سپس آن را اعمال کرد.\n", "index": 10, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# گزارش‎‌‌ها\n## گزارش تراز\n.\n* سال مالی: از طریق فیلتر سال مالی می توانید محدوده سال های مالی مورد نظر برای اجرای گزارش را تعیین نمایید.\n* نوع بازه زمانی: امکان تعیین بازه زمانی گزارش بر اساس دوره مالی یا تاریخ وجود دارد. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیق‌تر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\nنوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n* + افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند. پیش فرض همه انواع سند به جز اختتامیه و بستن حساب‌ها انتخاب شده است", "index": 29, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# گزارش‎‌‌ها\n## گزارش دفاتر\n. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیقتر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\n* نوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n+ افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند.\n* نوع حساب: میتوانید انتخاب کنید کدام انواع حساب ها در گزارش نمایش داده شوند که شامل موارد زیر هستند:\n* دائم\n* موقت\n* انتظامی\n* ویژگی حساب های معین: میتوانید انتخاب کنید که معین با کدام ویژگی نمایش داده شوند که شامل موارد زیر هستند", "index": 7, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# صدور سند حسابداری با ارز عملیاتی\n## اطلاعات سربرگ سند حسابداری\n* شعبه: لیست شعب فعال روی قفل شرکت که به آنها دسترسی داشته باشید، نمایش داده میشوند.\nدرصورتی که یک شعبه به عنوان شعبه پیش فرض کاربر انتخاب شده باشد، این شعبه در سند پر می‌شود و در صورت نیاز قابل تغییر است.\n* تاریخ: به صورت پیش فرض با تاریخ روز پر میشود. باید در محدوده سال مالی انتخابی و دوره مالی با وضعیت باز شده باشد.\n* نوع سند: برای اسناد صادر شده دستی در دفتر کل، با مقدار عمومی تکمیل شده است و قابل تغییر به انواع تعریف شده توسط کاربر است.\nبرای اسناد صادر شده از سایر ماژول ها، با نام ماژول صادر کننده سند تکمیل شده است .\n• امکان صدور سند با مقدار فیلد نوع سند افتتاحیه به صورت دستی تنها در اولین سال مالی وجود دارد.\n* شماره فرعی: شماره فرعی یک فیلد دستی و اختیاری است که شرکت ها میتوانند به دلایل مختلف مانند بایگانی یا ردیابی اسناد صادر شده، اقدام به ورود اطلاعات کنند. بر اساس تنظیمات سیستم میتوان یکتایی شماره فرعی را در سطح شرکت یا شعبه کنترل کرد. این کنترل برای همه اسناد از همه ماژول ها اعمال خواهد شد", "index": 9, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# قطعی کردن اسناد و صدور سند کل\n## صدور سند کل\nسند كل حاصل تجمیع سندهای قطعی صادرشده در سازمان، در یک بازه‌ی تاریخی مشخص است. سند كل معمولاً ماهانه صادر می‌شود. (برای دوره‌ی زمانی كوتاه‌تر از یک ماه و بیش از آن هم قابل صدور است). سازمانها بر اساس سند كل، دفتر روزنامه‌ی خود را كه یكی از دفاتر قانونی است تهیه می‌كنند.\nبرای صدور سند كل، ابتدا تمام اسناد حسابداری با وضعیت قطعی در محدوده‌ی تاریخی مشخص شده، بازیابی می‌شود. سپس مبالغ حساب‌های معین مربوط به هر حساب كل را به تفكیک مبلغ بدهكار/ بستانكار جمع كرده و نتیجه در حساب كل مربوطه نمایش داده می‌شود.\nبرای صدور سند کل از مسیر حسابداری مالی/ دفتر کل/ اسناد/ سند کل با انتخاب گزینه \"+\" به صفحه صدور سند کل می‌رویم. با انتخاب سند کل به فهرست اسناد کل می‌رویم و در آنجا نیز با انتخاب گزینه سند کل جدید، صفحه صدور سند کل را باز می‌کنیم.\nبر اساس تنظیمات کاربر، یعنی شرکت، دفتر و سال مالی باز می‌شود و قابل تغییر است. در صورتیکه این اطلاعات در پیش فرض مشخص نشده باشد، نیاز است توسط کاربر مشخص گردد.\nدر ابتدای صفحه توضیحات مربوط به دلیل صدور سند کل و الزامات آن آمده است. فیلتر های ذیل وجود دارد:\n* تاریخ / شماره سند: در این قسمت مشخص می شود که سند کل بر اساس تاریخ صادر شود یا شماره سند و پیش فرض بر اساس تاریخ است.\n* تاریخ: ابتدا و انتهای این تاریخ بر اساس کوچکترین و بزرگترین تاریخ اسناد قطعی شده نمایش داده می‌شود. تاریخ انتها قابل تغییر است.\n* روش صدور سند: در این قسمت روش صدور سند را از بین انواع کلی، روزانه، ماهانه و دوره‌ای قابل انتخاب است. پیش فرض ماهانه است. روش دوره‌ای بر اساس دوره‌های مالی تعریف در سال مالی صادر می‌شود.\n* صدور سند کل مجزا برای اسناد پایان سال: به صورت پیش فرض انتخاب شده است که به ازای اسناد پایان سال سندهای جداگانه صادر می‌شود.\nپس از مشخص کردن فیلتر های مورد نظر، گزینه صدور سند کل را انتخاب می‌کنیم و صفحه‌ای باز می‌شود که فرایند صدور را نمایش می‌دهد و در نهایت پس از اتمام عملیات پیام مناسب نمایش داده می‌شود.\n", "index": 3, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# معرفی دفتر\nبرای صدور سند حسابداری نیاز است دفتر در سیستم تعریف شود و ساختار حساب و ارز آن دفتر نیز مشخص گردد. برای اینکار از مسیر منوی اصلی/حسابداری مالی/ دفتر کل/ اطلاعات پایه/ دفتر را انتخاب می‌کنیم.\nفهرست دفترها باز می‌شود، با استفاده از گزینه جدید در بالا و سمت چپ صفحه به صفحه معرفی دفتر جدید می‌رویم.\nکد و عنوان دفتر را مشخص می‌کنیم، ساختار حساب را و ارز اصلی را انتخاب کرده و اگر این دفتر، دفتر اصلی سیستم است یعنی دفاتر قانونی شرکت با آن تهیه می‌شود، گزینه اصلی را انتخاب می‌کنیم.\nپس از آن صفحه ذخیره می‌شود.\nتصویر 1\n* در چند شرکتی دفتر در سطح گروه (مشترک) تعریف می‌شود و به شرکت‌ها گسترش داده می‌شود.\n", "index": 1, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه اطلاعات معین\n. در این فیلد میتوانید ماژول های مجاز به استفاده از معین مربوطه را مشخص کنید، بعد از انتخاب هر ماژول ، امکان انتخاب در فرم های استقرار حساب ماژول ها و صدور سند حسابداری با معین جاری در ماژول مورد نظر به کاربر داده می شود .\n* اگر بعد از استفاده ( در دفتر کل یا سایر ماژول ها ) امکان صدور سند از ماژول ها برداشته شود، در زمان صدور سند حسابداری از سمت همان ماژول کنترل می شود که معین های دارای این ویژگی استفاده شده باشند .\n* امکان مشاهده اطلاعات همه معین ها در گزارشات دفتر کل ( فارغ از اینکه امکان استفاده در دفتر کل برای آنها انتخاب شده باشد یا نه ) وجود دارد\n* **فعال:** وضعیت حساب معین را نمایش می دهد که می تواند فعال یا غیرفعال باشد.\nحساب معینی که گزینه \"فعال\" آن انتخاب نشده باشد، امکان شرکت در هیچ عملیاتی از جمله صدور سند حسابداری، نگاشت حساب ها، حساب های طرف مقابل، نخواهد داشت.\n* حساب های معین همواره امکان غیر فعال شدن دارند، در صورت فعال نبودن، در زمان صدور سند حسابداری های سیستمی اجازه صدور سند داده نمی‌شود", "index": 16, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# انوع سند حسابداری\nثبت کلیه رویدادهای مالی اعم از خرید و فروش، دریافت تسهیلات مالی، عملیات دریافت و پرداخت وجوه مالی و.... در قالب اسناد حسابداری انجام می‌شود؛ لذا متمایز بودن و امکان دسته بندی اسناد حسابدری حائز اهمیت خواهد بود تا بتوان جهت گزارشگری، بررسی و کنترل‌های داخلی از آن استفاده کرد. اين امكان در قالب انواع مختلف سند حسابداري در سیستم طراحی شده است و در هنگام ثبت اسناد حسابداري نوع آن به صورت دستی یا اتوماتیک مشخص می‌شود. انواع سند به چهار دسته کلی تقسیم می‌شوند:\n1. اسناد دستی صادر شده از دفتر کل که با نوع عمومی شناخته می‌شوند.\n2. اسناد سیستمی صادر شده از دفتر کل که شامل تسعیر ارز، عملیات پایان سال و .... می‌باشد.\n3. اسناد صادر شده از سایر ماژول‌ها ناشی از عملیات مرتبط با خرید، فروش انبار و غیره. نوع سند در این نوع از اسناد با توجه به ماژول مورد نظر به صورت خودکار ایجاد می‌شود. مانند: سند انبار، فروش، خزانه داری و ...\n4. اسناد دستی صادر شده از دفتر کل که کاربر نیاز دارد با نوع دلخواه خود جهت نیازمندی‌های گزارشگری تعریف کند", "index": 15, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# انوع سند حسابداری\n. ثبت می شود و با نوع ماژولی که از آن صادر می شوند، شناسایی می‌شوند. |\nدر صورتیکه کاربر نیاز داشته باشد یک نوع سند جدید در سیستم تعریف کند، از مسیر منو اصلی/ حسابداری مالی/ دفتر کل/ اسناد / نوع سند، کلید \"+\" را انتخاب می‎‌شود.\nتصویر 1\nبا انتخاب کلید\"+\" در نوع سند یک فرم به صورت \"تصویر 2\" باز می‌شود. عنوان مورد نظر مشخص می‌شود در صورت نیاز توضیحات نیز وارد می‌شود این مورد اجباری نیست سپس با انتخاب کلید ذخیره از گوشه سمت چپ و بالا، نوع سند ذخیره خواهد شد.\nتصویر 2\nانواع سندهای سیستمی شامل عمومی، عملیات پایان سال، بستن حساب‌ها و تسعیر ارز و ....، همچنین نوع سندهای مربوط به سایر ماژول‌ها توسط کاربران قابل ویرایش و حذف نیستد اما انواع سند ایجاد شده توسط کاربران، تا قبل از استفاده قابل حذف و ویرایش است. پس از استفاده نیز می‌توان با غیر فعال کردن نوع سند از استفاده آن جلوگیری کرد", "index": 2, "module": "دفتر کل", "source": "voucher.csv"}]

    # Mock the instance of Retriever
    mock_retriever_instance = MagicMock()
    # Mock the async method on the instance
    mock_retriever_instance.retrieve_context = AsyncMock(return_value=expected_context)
    
    # Make the patched class return our mock instance
    mock_retriever_class.return_value = mock_retriever_instance

    # 2. Act
    result = await retrieve_context_with_metadata(
        query=mock_query, 
        input_modules=mock_modules
    )

    # 3. Assert
    assert result == expected_context

    # Check the class was instantiated
    mock_retriever_class.assert_called_once_with()
    
    # Check the retrieve_context method was called with the correct args
    mock_retriever_instance.retrieve_context.assert_called_once_with(
        mock_query, 
        module_filter=mock_modules
    )

@pytest.mark.asyncio
@patch("src.logic.Retriever")
async def test_retrieve_context_with_database_index(mock_retriever_class):
    """
    Tests the 'elif database_index:' branch.
    Ensures 'retrieve_context' is called with 'database_index' as a positional arg.
    """
    # 1. Arrange
    mock_query = 'روش ثبت خرید کالا در انبار به چه صورته؟'
    mock_index = '../VectorDB'
    expected_context = [{"text": "# قیمت سند انبار\n## مشاهده قیمت سند انبار\n.\nفیلدهای تاریخ سند، شماره سند، عنوان سند و عنوان انبار غیرقابل تغییر می باشد. در صورت داشتن لایسنس ارزی امکان تغییر ارز از طریق سلکتور ارز، برای ثبت قیمت سند خرید خارجی وجود دارد.\nکاربر در فیلد فی قیمت واحد کالا را وارد کرده و سیستم با توجه به تعداد کالا، مبلغ را محاسبه می نماید. در صورتی که کاربر نیاز به ثبت تخفیف و کرایه حمل داشته باشد از طریق گزینه عوامل مبلغی اقدام می نماید.\nدر فرم عوامل مبلغی کاربر امکان تعیین درصد یا مبلغ تخفیف و کرایه حمل وجود دارد و سیستم محاسبات آنرا انجام می دهد.\nبرای محاسبه مالیات بر ارزش افزوده، پیش نیازهای زیر لازم است که در حسابداری مالیاتی تعریف می گردد:\n* تعریف گروه مالیاتی کالا\n* تخصیص گروه مالیاتی به کالا\n* تعریف گروه مالیاتی طرف تجاری\n* تخصیص گروه مالیاتی به طرف تجاری\n* تعریف نرخ مالیات بر ارزش افزوده برای گروه های مالیاتی کالا و طرف تجاری\nدر صورتی که موارد فوق تعیین نشده باشد کاربر با پیام خطا مواجه می شود.", "index": 35, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. این گزینه به عنوان تسهیلات کاربری استفاده می شود برای اینکه در صورتی که کاربر نیاز به رسید یا حواله اجزای یک کالای کلی داشته باشد به جای اینکه همه ان اجزا را در فرم سند انبار انتخاب نماید، کالای اصلی و کلی را انتخاب کرده و خود سیستم با توجه به فرمول انتخابی اجزای کالا را به کاربر نمایش دهد . در این حالیت انباردار می تواند در صورت نیاز مقادیر آنرا نیز ویرایش نماید. این گزینه صرفا تسهیلات کاربری بوده و تغییری در موجودی کالای اصلی بوجود نمی اید. با این امکان در زمان ثبت اسناد صرفه جویی شده و اشتباهات کاربری ناشی از فراموشی انتخاب یکی از اجزای کالا کاهش می باشد.\nدر بخش سایدبار سند انبار جمع کل اقلام سند به واحدهای ثبت سند، واحد اصلی و واحد دوم نمایش داده می شود.\nدر صورتی که سند انبار دارای اسناد مرتبط باشد نیز **پس از ذخیره سند** در بخش سایدبار نمایش داده می شود.\nدر صورتی که یکی از ردیف های سند انبار انتخاب گردد، در قسمت ساید بار مشخصات تکمیلی کالا شامل طبقه حساب کالا، نوع کالا، نوع کارکرد کالا و ویژگی های سطح کالا نمایش داده می شود", "index": 16, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. در این لیست تنها طرف مقابل هایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد طرف مقابل نمایش داده می شود :\n* طرف مقابل متعلق به شرکت انتخابی باشد.\n* طرف مقابل فعال باشد.\n* طرف مقابل ها بر اساس نوع طرف مقابل تعیین شده در تنظیمات الگوی سند انبار می باشد.\n* طرف مقابل در صورتی که شخص حقیقی یا حقوقی است، دارای نقش تعیین شده در تنظیمات الگوی سند انبار باشد.\nتاریخ: تاریخ ثبت سند انبار در این فیلد انتخاب می گردد. موجودی کالا در این تاریخ با توجه به نوع سند انبار افزایش یا کاهش می یابد. انتخاب تاریخ در سند انبار اجباری است.\nشماره: در صورتی که برای اسناد، روش شماره گذاری تعریف شده باشد، شماره سند به صورت اتوماتیک بر اساس همان روش مقداردهی می شود ولی در صورتی که روش شماره گذاری وجود نداشته باشد، این شماره توسط انباردار به صورت دستی وارد می شود. ثبت شماره در سند انبار اجباری است.\nتوضیحات: در توضیحات، شرح سند انبار به صورت اختیاری می تواند وارد گردد", "index": 9, "module": "انبار", "source": "inventory.csv"}, {"text": "# انبارگردانی\n## مراحل انبارگردانی\n.\nبا توجه به اینکه همه اطلاعات مورد نیاز برای ثبت اسناد انبار وجود دارد، اینگونه مغایرت ها \"مغایرت آماده ثبت\" می باشند بدین معنی که سیستم بدون هیچگونه اخذ اطلاعات تکمیلی از کاربر می تواند اسناد انبار را ثبت نماید ولی در صورتی که داده های مورد نیاز برای ثبت اتوماتیک اسناد انبار را نداشته باشد، پیشنویس اسناد انبار به کاربر نمایش داده شده و کاربر می تواند داده های مورد نیاز آنرا تکمیل نماید، اینگونه مغایرت ها که به داده های کاربر برای ثبت سند نیاز دارد در بخش \"مغایرت نیازمند به تکمیل\" نمایش داده می شود. بخش \"مغایرت نیازمند به تکمیل\" شامل کالاهایی ست که دارای واحد دوم بوده و داده های واحد دوم در انبارگردانی ثبت نشده است و یا کالاهایی که دارای عامل کنترل موجودی است و ثبت اسناد نیازمند انتخاب عامل کنترل موجودی توسط کاربر است و یا کالاهایی که دارای ویژگی ثبت سند اجباری است و ثبت اسناد نیازمند انتخاب ویژگی ثبت سند توسط کاربر است و یا کالاهای با روش قیمت گذاری شناسایی ویژه تعریف شده اند که نیازمند ثبت عطف می باشند.\nلازم به ذکر است گزینه عامل کنترل موجودی در صورت داشتن لایسنس نمایش داده می شود.\n1", "index": 32, "module": "انبار", "source": "inventory.csv"}, {"text": "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** نشانی تحویل: نشانی که قرار است کالا / خدمت در آن تحویل داده شود را از میان \"نشانی های مشتری که بعنوان نشانی تحویل تعریف شده است\"، انتخاب می نماییم.\n** توضیحات تحویل: در صورت نیاز به توضیحات اضافه، توضیحات تحویل را میتوان وارد نمود.\nنکته: اطلاعات تحویل در صورت نیاز، میتواند به ازای قلم های مختلف سفارش، متفاوت تعریف شود.\nپس از پر کردن اطلاعات اصلی سفارش، اقلام سفارش را ثبت می نماییم. به ازای هر کالا یا خدمت یک قلم در سفارش ثبت می نماییم. در ادامه نحوه ثبت اقلام را توضیح میدهیم:\n* ابتدا دکمه \"ایجاد\" را زده تا یک قلم جدید ایجاد شود.\n* قلم: در فیلد قلم، کالا یا خدمت مورد نظر را انتخاب می نماییم.\nنکته: در این لیست کالا/ خدمت هایی قابل مشاهده است که شرایط زیر را داشته باشد:\n** کلیه خدماتی که در شرکت تعریف شده و وضعیت فعال داشته باشند.\n** کالاهایی که کارکرد آن در شرکت جاری، قابل فروش بوده و وضعیت فعال داشته باشد. همچنین انبار مرتبط با کالا باید به حوزه فروش فاکتور جاری مرتبط شده باشد.\n* واحد سنجش: با انتخاب قلم مورد نظر (کالا یا خدمت)، با واحد سنجش پیش فرض کالا یا خدمت در قلم پر میشود", "index": 26, "module": "فروش", "source": "sales.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\nبرای ثبت سند انبار از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای ثبت سند انبار ابتدا لازم است شرکت و الگوی مناسب برای ثبت سند اتخاب شود. در صورتی که الگو و شرکت انتخابی برای کاربر، جزو موارد پرکاربرد برای کاربر است، کاربر می تواند افزودن به منو را انتخاب کرده و در این حالت یک منو با عنوان الگوهای سند منتخب به منو اضافه شده و در زیر آن الگوی انتخابی اضافه می گردد.\nبرای ثبت سند انبار فیلدهای زیر تکمیل می گردد:\nانبار: نام انباری است که کالای خریداری شده لازم است در آن رسید گردد، انتخاب شود. انتخاب انبار اجباری است. در این لیست تنها انبارهایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد انبار نمایش داده می شود :\n* انبار متعلق به شرکت انتخابی باشد.\n* انبار فعال باشد.\n* الگوی انتخابی در لیست الگوهای مجاز آن انبارهای باشد.\nطرف مقابل: لیست همه طرف مقابل ها با توجه به الگوی انتخابی و تنظیمات الگو نمایش داده می شود", "index": 1, "module": "انبار", "source": "inventory.csv"}, {"text": "# انبارگردانی\n## مراحل انبارگردانی\n. در این حالت باز هم کاربر می تواند لیست کالاهای انبارگردانی را ویرایش کرده و از طریق تب لیست کالاهای انبارگردانی و گزینه های افزودن کالاهای انبارگردانی و یا بارگذاری از اکسل، کالاهایی را جهت انبارگردانی انتخاب نماید.\nدر صورت افزودن کالای جدید، این کالا فاقد تگ بوده و نیاز است برای ادامه و استفاده در شمارش به آن تگ بدهد. بنابراین از طریق گزینه صدور تگ، برای کالاهای جدید تگ صادر می نماید.\nدرصورتی که کالا تگ داشته باشد در تبهای شمارش، از طریق گزینه افزودن کالا، این کالا به لیست شمارش اضافه می گردد.\nبا انتخاب گزینه افزودن کالا، لیست کالاهایی که پس از شروع انبارگردانی به لیست کالاها اضافه شده اند نمایش داده شده و کاربر می تواند آنها را انتخاب نماید.\nپس از انتخاب کالا، این کالاها به لیست شمارش اضافه می شود.\n1. **ثبت نتایج شمارش:**\nکاربر می تواند به 3 روش اقدام به ثبت شمارش انبارگردانی نماید:\n1. کاربر می تواند با استفاده از گزینه ی \" **ثبت مقادیر با تگ**\" نتایج شمارش را در سیستم ثبت نماید.\n2. کاربر می تواند با استفاده از گزینه ی **دریافت و ارسال اکسل**، نتایج شمارش را در سیستم ثبت نماید.\n3", "index": 10, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. در صورتی که کالا دارای واحد سنجش دوم باشد، مقدار به واحد سنجش دوم نیز لازم است مقداردهی گردد. در هر سند تنها لیست کالاهایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد کالا نمایش داده می شود :\n* کالا متعلق به شرکت انتخابی باشد.\n* کالا فعال باشد.\n* نوع کارکرد کالای تنظیم شده در الگوی سند انتخابی با نوع کارکرد کالا برابر باشد.\n* نوع انبار برای انبار انتخابی با نوع انبار تعیین شده برای کالا برابر باشد.\nدر صورتی که اطلاعات تکمیلی سند انبار برای ثبت در قلم تنظیم شده باشد ، این فیلدها برای مقداردهی در قلم سند انبار نیز نمایش داده می شود.\nبرای ثبت اقلام انبار می توان علاوه بر استفاده از گزینه جدید و ثبت کالا، از گزینه افزودن با اجزا کالا استفاده کرد. در این گزینه کاربر می تواند عنوان و مقدار کالایی را انتخاب نماید که قبلا اجزا و فرمول ان را در سیستم تعریف کرده است", "index": 3, "module": "انبار", "source": "inventory.csv"}, {"text": "# ثبت درخواست کالا از انبار\n## مراحل ثبت درخواست کالا از انبار\nبرای تعریف درخواست کالا در ماژول لجستیک، از منو انبار و حسابداری انبار، اطلاعات پایه، کالا، گزینه درخواست کالا (+) را انتخاب نمایید.\nبرای ثبت درخواست کالا ابتدا نوع درخواست میبایست انتخاب گردد که عبارتند از مصرف، تولید، انتقال بین انبار، امانی، ضایعات، دارایی ثابت و سایر. سپس از لیست مراکز نگهداری تعریف شده در سیستم، مرکز نگهداری مورد نظر انتخاب می گردد. تاریخ نیاز فیلد اجباری بوده و کاربر مشخص می کند که کالای درخواستی را در چه تاریخی به آن نیاز دارد، این فیلد جهت تاکید به مسئول انبار می باشد و کاربر انبار آن کالا را می تواند تا پیش از تاریخ موعود، در تاریخ نیاز و پس از تاریخ مورد نیاز با تاخیر ارسال نماید. تاریخ ثبت سند فیلد اجباری می باشد که نشان می دهد درخواست دهنده در چه تاریخی درخواست خود را در سیستم ثبت می نماید. فیلد درخواست کننده نیز اجباری می باشد و کاربر از لیست اشخاص تعریف شده در سیستم با نقش \"کارمند\" ، نام درخواست کننده را انتخاب می نماید. فیلدهای مرکز نگهداری فرستنده، انبار فرستنده و شماره غیر قابل ویرایش می باشند. شماره درخواست توسط الگوی شماره گذاری تعریف شده در بخش عمومی سیستم قابل تنظیم می باشد و می تواند به صورت خودکار و دستی تنظیم شده تا کاربر بتواند در فرم درخواست کالا، شماره درخواست خود ار تغییر بدهد.\nاطلاعات قلم سند انبار با انتخاب کالا و انتخاب واحد سنجش آن کالا انجام می شود. با توجه به واحد سنجش انتخاب شده، مقدار کالا وارد می شود. در صورتی که کالا دارای واحد سنجش دوم باشد، مقدار به واحد سنجش دوم نیز لازم است مقداردهی گردد.\nدر بخش سایدبار درخواست کالا جمع کل اقلام سند به واحدهای ثبت سند، واحد اصلی و واحد دوم نمایش داده می شود.\nدر صورتی که درخواست کالا دارای اسناد مرتبط مانند سند مصرف مرکز باشد **پس از ذخیره سند** در بخش سایدبار نمایش داده می شود.\nدر صورتی که یکی از ردیف های سند انبار انتخاب گردد، در قسمت ساید بار مشخصات تکمیلی کالا شامل طبقه حساب کالا، نوع کالا، نوع کارکرد کالا و ویژگی های سطح کالا نمایش داده می شود.\nگزینه های بالای صفحه ی ثبت سند جدید به شرح زیر می باشد:\n1. نام شرکت: شرکتی را که در آن ثبت درخواست کالا را انجام می دهیم نمایش داده می شود که بر اساس شرکت انتخاب شده در فرم مودال باز شده، نمایش داده می شود و قابل تغییر نمی باشد.\n2. ذخیره: این گزینه امکان \"ذخیره\" و \"ذخیره و جدید\" سند درخواست کالا را فراهم می کند.\n3. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم درخواست کالا را فراهم می کند.\n4. سایر عملیات: این گزینه امکان درخواست کالای جدید و نمایش فهرست درخواست های کالا را فراهم می سازد. گزینه اقلام سند نیز رکوردهای اقلام سند درخواست کالا را به کاربر نمایش می دهد.\n", "index": 2, "module": "انبار", "source": "inventory.csv"}, {"text": "# ثبت درخواست کالا از انبار\nدر سازمان‌ها، واحدهای مختلف برای انجام فعالیت‌های تولیدی و خدماتی خود به کالا و تجهیزات نیاز دارند. این نیازها به صورت رسمی از طریق فرم‌های درخواست کالا به انبار اعلام می‌شود. برای تامین کالاهای مورد نیاز در سازمان، واحدهای مختلف فرم درخواست کالا را در سیستم تکمیل کرده و به انبار ارسال می‌کنند. انباردار پس از بررسی درخواست، تایید و تطبیق آن با موجودی انبار، در صورت موجود بودن کالا، آن را تحویل داده و موجودی انبار را کسر می‌کند و در غیر این صورت، درخواست را به سیستم خرید جهت ثبت سفارش جدید ارجاع می‌دهد.\n\n## فهرست درخواست کالا از انبار\n## مراحل ثبت درخواست کالا از انبار", "index": 0, "module": "انبار", "source": "inventory.csv"}]

    # Mock the instance and its async method
    mock_retriever_instance = MagicMock()
    mock_retriever_instance.retrieve_context = AsyncMock(return_value=expected_context)
    mock_retriever_class.return_value = mock_retriever_instance

    # 2. Act
    # We pass input_modules=None to ensure we skip the first 'if' block
    result = await retrieve_context_with_metadata(
        query=mock_query,  
        database_index=mock_index
    )

    # 3. Assert
    assert result == expected_context
    mock_retriever_class.assert_called_once_with()
    
    # Check the method was called with the correct positional argument
    mock_retriever_instance.retrieve_context.assert_called_once_with(
        mock_query, 
        mock_index
    )

@pytest.mark.asyncio
@patch("src.logic.Retriever")
async def test_retrieve_context_with_no_filters(mock_retriever_class):
    """
    Tests the 'else:' branch (default case).
    Ensures 'retrieve_context' is called with only the query.
    """
    # 1. Arrange
    mock_query = 'روش ثبت خرید کالا در انبار به چه صورته؟'
    mock_index = None
    expected_context = [{"text": "# قیمت سند انبار\n## مشاهده قیمت سند انبار\n.\nفیلدهای تاریخ سند، شماره سند، عنوان سند و عنوان انبار غیرقابل تغییر می باشد. در صورت داشتن لایسنس ارزی امکان تغییر ارز از طریق سلکتور ارز، برای ثبت قیمت سند خرید خارجی وجود دارد.\nکاربر در فیلد فی قیمت واحد کالا را وارد کرده و سیستم با توجه به تعداد کالا، مبلغ را محاسبه می نماید. در صورتی که کاربر نیاز به ثبت تخفیف و کرایه حمل داشته باشد از طریق گزینه عوامل مبلغی اقدام می نماید.\nدر فرم عوامل مبلغی کاربر امکان تعیین درصد یا مبلغ تخفیف و کرایه حمل وجود دارد و سیستم محاسبات آنرا انجام می دهد.\nبرای محاسبه مالیات بر ارزش افزوده، پیش نیازهای زیر لازم است که در حسابداری مالیاتی تعریف می گردد:\n* تعریف گروه مالیاتی کالا\n* تخصیص گروه مالیاتی به کالا\n* تعریف گروه مالیاتی طرف تجاری\n* تخصیص گروه مالیاتی به طرف تجاری\n* تعریف نرخ مالیات بر ارزش افزوده برای گروه های مالیاتی کالا و طرف تجاری\nدر صورتی که موارد فوق تعیین نشده باشد کاربر با پیام خطا مواجه می شود.", "index": 35, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. این گزینه به عنوان تسهیلات کاربری استفاده می شود برای اینکه در صورتی که کاربر نیاز به رسید یا حواله اجزای یک کالای کلی داشته باشد به جای اینکه همه ان اجزا را در فرم سند انبار انتخاب نماید، کالای اصلی و کلی را انتخاب کرده و خود سیستم با توجه به فرمول انتخابی اجزای کالا را به کاربر نمایش دهد . در این حالیت انباردار می تواند در صورت نیاز مقادیر آنرا نیز ویرایش نماید. این گزینه صرفا تسهیلات کاربری بوده و تغییری در موجودی کالای اصلی بوجود نمی اید. با این امکان در زمان ثبت اسناد صرفه جویی شده و اشتباهات کاربری ناشی از فراموشی انتخاب یکی از اجزای کالا کاهش می باشد.\nدر بخش سایدبار سند انبار جمع کل اقلام سند به واحدهای ثبت سند، واحد اصلی و واحد دوم نمایش داده می شود.\nدر صورتی که سند انبار دارای اسناد مرتبط باشد نیز **پس از ذخیره سند** در بخش سایدبار نمایش داده می شود.\nدر صورتی که یکی از ردیف های سند انبار انتخاب گردد، در قسمت ساید بار مشخصات تکمیلی کالا شامل طبقه حساب کالا، نوع کالا، نوع کارکرد کالا و ویژگی های سطح کالا نمایش داده می شود", "index": 16, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. در این لیست تنها طرف مقابل هایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد طرف مقابل نمایش داده می شود :\n* طرف مقابل متعلق به شرکت انتخابی باشد.\n* طرف مقابل فعال باشد.\n* طرف مقابل ها بر اساس نوع طرف مقابل تعیین شده در تنظیمات الگوی سند انبار می باشد.\n* طرف مقابل در صورتی که شخص حقیقی یا حقوقی است، دارای نقش تعیین شده در تنظیمات الگوی سند انبار باشد.\nتاریخ: تاریخ ثبت سند انبار در این فیلد انتخاب می گردد. موجودی کالا در این تاریخ با توجه به نوع سند انبار افزایش یا کاهش می یابد. انتخاب تاریخ در سند انبار اجباری است.\nشماره: در صورتی که برای اسناد، روش شماره گذاری تعریف شده باشد، شماره سند به صورت اتوماتیک بر اساس همان روش مقداردهی می شود ولی در صورتی که روش شماره گذاری وجود نداشته باشد، این شماره توسط انباردار به صورت دستی وارد می شود. ثبت شماره در سند انبار اجباری است.\nتوضیحات: در توضیحات، شرح سند انبار به صورت اختیاری می تواند وارد گردد", "index": 9, "module": "انبار", "source": "inventory.csv"}, {"text": "# انبارگردانی\n## مراحل انبارگردانی\n.\nبا توجه به اینکه همه اطلاعات مورد نیاز برای ثبت اسناد انبار وجود دارد، اینگونه مغایرت ها \"مغایرت آماده ثبت\" می باشند بدین معنی که سیستم بدون هیچگونه اخذ اطلاعات تکمیلی از کاربر می تواند اسناد انبار را ثبت نماید ولی در صورتی که داده های مورد نیاز برای ثبت اتوماتیک اسناد انبار را نداشته باشد، پیشنویس اسناد انبار به کاربر نمایش داده شده و کاربر می تواند داده های مورد نیاز آنرا تکمیل نماید، اینگونه مغایرت ها که به داده های کاربر برای ثبت سند نیاز دارد در بخش \"مغایرت نیازمند به تکمیل\" نمایش داده می شود. بخش \"مغایرت نیازمند به تکمیل\" شامل کالاهایی ست که دارای واحد دوم بوده و داده های واحد دوم در انبارگردانی ثبت نشده است و یا کالاهایی که دارای عامل کنترل موجودی است و ثبت اسناد نیازمند انتخاب عامل کنترل موجودی توسط کاربر است و یا کالاهایی که دارای ویژگی ثبت سند اجباری است و ثبت اسناد نیازمند انتخاب ویژگی ثبت سند توسط کاربر است و یا کالاهای با روش قیمت گذاری شناسایی ویژه تعریف شده اند که نیازمند ثبت عطف می باشند.\nلازم به ذکر است گزینه عامل کنترل موجودی در صورت داشتن لایسنس نمایش داده می شود.\n1", "index": 32, "module": "انبار", "source": "inventory.csv"}, {"text": "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** نشانی تحویل: نشانی که قرار است کالا / خدمت در آن تحویل داده شود را از میان \"نشانی های مشتری که بعنوان نشانی تحویل تعریف شده است\"، انتخاب می نماییم.\n** توضیحات تحویل: در صورت نیاز به توضیحات اضافه، توضیحات تحویل را میتوان وارد نمود.\nنکته: اطلاعات تحویل در صورت نیاز، میتواند به ازای قلم های مختلف سفارش، متفاوت تعریف شود.\nپس از پر کردن اطلاعات اصلی سفارش، اقلام سفارش را ثبت می نماییم. به ازای هر کالا یا خدمت یک قلم در سفارش ثبت می نماییم. در ادامه نحوه ثبت اقلام را توضیح میدهیم:\n* ابتدا دکمه \"ایجاد\" را زده تا یک قلم جدید ایجاد شود.\n* قلم: در فیلد قلم، کالا یا خدمت مورد نظر را انتخاب می نماییم.\nنکته: در این لیست کالا/ خدمت هایی قابل مشاهده است که شرایط زیر را داشته باشد:\n** کلیه خدماتی که در شرکت تعریف شده و وضعیت فعال داشته باشند.\n** کالاهایی که کارکرد آن در شرکت جاری، قابل فروش بوده و وضعیت فعال داشته باشد. همچنین انبار مرتبط با کالا باید به حوزه فروش فاکتور جاری مرتبط شده باشد.\n* واحد سنجش: با انتخاب قلم مورد نظر (کالا یا خدمت)، با واحد سنجش پیش فرض کالا یا خدمت در قلم پر میشود", "index": 26, "module": "فروش", "source": "sales.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\nبرای ثبت سند انبار از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای ثبت سند انبار ابتدا لازم است شرکت و الگوی مناسب برای ثبت سند اتخاب شود. در صورتی که الگو و شرکت انتخابی برای کاربر، جزو موارد پرکاربرد برای کاربر است، کاربر می تواند افزودن به منو را انتخاب کرده و در این حالت یک منو با عنوان الگوهای سند منتخب به منو اضافه شده و در زیر آن الگوی انتخابی اضافه می گردد.\nبرای ثبت سند انبار فیلدهای زیر تکمیل می گردد:\nانبار: نام انباری است که کالای خریداری شده لازم است در آن رسید گردد، انتخاب شود. انتخاب انبار اجباری است. در این لیست تنها انبارهایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد انبار نمایش داده می شود :\n* انبار متعلق به شرکت انتخابی باشد.\n* انبار فعال باشد.\n* الگوی انتخابی در لیست الگوهای مجاز آن انبارهای باشد.\nطرف مقابل: لیست همه طرف مقابل ها با توجه به الگوی انتخابی و تنظیمات الگو نمایش داده می شود", "index": 1, "module": "انبار", "source": "inventory.csv"}, {"text": "# انبارگردانی\n## مراحل انبارگردانی\n. در این حالت باز هم کاربر می تواند لیست کالاهای انبارگردانی را ویرایش کرده و از طریق تب لیست کالاهای انبارگردانی و گزینه های افزودن کالاهای انبارگردانی و یا بارگذاری از اکسل، کالاهایی را جهت انبارگردانی انتخاب نماید.\nدر صورت افزودن کالای جدید، این کالا فاقد تگ بوده و نیاز است برای ادامه و استفاده در شمارش به آن تگ بدهد. بنابراین از طریق گزینه صدور تگ، برای کالاهای جدید تگ صادر می نماید.\nدرصورتی که کالا تگ داشته باشد در تبهای شمارش، از طریق گزینه افزودن کالا، این کالا به لیست شمارش اضافه می گردد.\nبا انتخاب گزینه افزودن کالا، لیست کالاهایی که پس از شروع انبارگردانی به لیست کالاها اضافه شده اند نمایش داده شده و کاربر می تواند آنها را انتخاب نماید.\nپس از انتخاب کالا، این کالاها به لیست شمارش اضافه می شود.\n1. **ثبت نتایج شمارش:**\nکاربر می تواند به 3 روش اقدام به ثبت شمارش انبارگردانی نماید:\n1. کاربر می تواند با استفاده از گزینه ی \" **ثبت مقادیر با تگ**\" نتایج شمارش را در سیستم ثبت نماید.\n2. کاربر می تواند با استفاده از گزینه ی **دریافت و ارسال اکسل**، نتایج شمارش را در سیستم ثبت نماید.\n3", "index": 10, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. در صورتی که کالا دارای واحد سنجش دوم باشد، مقدار به واحد سنجش دوم نیز لازم است مقداردهی گردد. در هر سند تنها لیست کالاهایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد کالا نمایش داده می شود :\n* کالا متعلق به شرکت انتخابی باشد.\n* کالا فعال باشد.\n* نوع کارکرد کالای تنظیم شده در الگوی سند انتخابی با نوع کارکرد کالا برابر باشد.\n* نوع انبار برای انبار انتخابی با نوع انبار تعیین شده برای کالا برابر باشد.\nدر صورتی که اطلاعات تکمیلی سند انبار برای ثبت در قلم تنظیم شده باشد ، این فیلدها برای مقداردهی در قلم سند انبار نیز نمایش داده می شود.\nبرای ثبت اقلام انبار می توان علاوه بر استفاده از گزینه جدید و ثبت کالا، از گزینه افزودن با اجزا کالا استفاده کرد. در این گزینه کاربر می تواند عنوان و مقدار کالایی را انتخاب نماید که قبلا اجزا و فرمول ان را در سیستم تعریف کرده است", "index": 3, "module": "انبار", "source": "inventory.csv"}, {"text": "# ثبت درخواست کالا از انبار\n## مراحل ثبت درخواست کالا از انبار\nبرای تعریف درخواست کالا در ماژول لجستیک، از منو انبار و حسابداری انبار، اطلاعات پایه، کالا، گزینه درخواست کالا (+) را انتخاب نمایید.\nبرای ثبت درخواست کالا ابتدا نوع درخواست میبایست انتخاب گردد که عبارتند از مصرف، تولید، انتقال بین انبار، امانی، ضایعات، دارایی ثابت و سایر. سپس از لیست مراکز نگهداری تعریف شده در سیستم، مرکز نگهداری مورد نظر انتخاب می گردد. تاریخ نیاز فیلد اجباری بوده و کاربر مشخص می کند که کالای درخواستی را در چه تاریخی به آن نیاز دارد، این فیلد جهت تاکید به مسئول انبار می باشد و کاربر انبار آن کالا را می تواند تا پیش از تاریخ موعود، در تاریخ نیاز و پس از تاریخ مورد نیاز با تاخیر ارسال نماید. تاریخ ثبت سند فیلد اجباری می باشد که نشان می دهد درخواست دهنده در چه تاریخی درخواست خود را در سیستم ثبت می نماید. فیلد درخواست کننده نیز اجباری می باشد و کاربر از لیست اشخاص تعریف شده در سیستم با نقش \"کارمند\" ، نام درخواست کننده را انتخاب می نماید. فیلدهای مرکز نگهداری فرستنده، انبار فرستنده و شماره غیر قابل ویرایش می باشند. شماره درخواست توسط الگوی شماره گذاری تعریف شده در بخش عمومی سیستم قابل تنظیم می باشد و می تواند به صورت خودکار و دستی تنظیم شده تا کاربر بتواند در فرم درخواست کالا، شماره درخواست خود ار تغییر بدهد.\nاطلاعات قلم سند انبار با انتخاب کالا و انتخاب واحد سنجش آن کالا انجام می شود. با توجه به واحد سنجش انتخاب شده، مقدار کالا وارد می شود. در صورتی که کالا دارای واحد سنجش دوم باشد، مقدار به واحد سنجش دوم نیز لازم است مقداردهی گردد.\nدر بخش سایدبار درخواست کالا جمع کل اقلام سند به واحدهای ثبت سند، واحد اصلی و واحد دوم نمایش داده می شود.\nدر صورتی که درخواست کالا دارای اسناد مرتبط مانند سند مصرف مرکز باشد **پس از ذخیره سند** در بخش سایدبار نمایش داده می شود.\nدر صورتی که یکی از ردیف های سند انبار انتخاب گردد، در قسمت ساید بار مشخصات تکمیلی کالا شامل طبقه حساب کالا، نوع کالا، نوع کارکرد کالا و ویژگی های سطح کالا نمایش داده می شود.\nگزینه های بالای صفحه ی ثبت سند جدید به شرح زیر می باشد:\n1. نام شرکت: شرکتی را که در آن ثبت درخواست کالا را انجام می دهیم نمایش داده می شود که بر اساس شرکت انتخاب شده در فرم مودال باز شده، نمایش داده می شود و قابل تغییر نمی باشد.\n2. ذخیره: این گزینه امکان \"ذخیره\" و \"ذخیره و جدید\" سند درخواست کالا را فراهم می کند.\n3. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم درخواست کالا را فراهم می کند.\n4. سایر عملیات: این گزینه امکان درخواست کالای جدید و نمایش فهرست درخواست های کالا را فراهم می سازد. گزینه اقلام سند نیز رکوردهای اقلام سند درخواست کالا را به کاربر نمایش می دهد.\n", "index": 2, "module": "انبار", "source": "inventory.csv"}, {"text": "# ثبت درخواست کالا از انبار\nدر سازمان‌ها، واحدهای مختلف برای انجام فعالیت‌های تولیدی و خدماتی خود به کالا و تجهیزات نیاز دارند. این نیازها به صورت رسمی از طریق فرم‌های درخواست کالا به انبار اعلام می‌شود. برای تامین کالاهای مورد نیاز در سازمان، واحدهای مختلف فرم درخواست کالا را در سیستم تکمیل کرده و به انبار ارسال می‌کنند. انباردار پس از بررسی درخواست، تایید و تطبیق آن با موجودی انبار، در صورت موجود بودن کالا، آن را تحویل داده و موجودی انبار را کسر می‌کند و در غیر این صورت، درخواست را به سیستم خرید جهت ثبت سفارش جدید ارجاع می‌دهد.\n\n## فهرست درخواست کالا از انبار\n## مراحل ثبت درخواست کالا از انبار", "index": 0, "module": "انبار", "source": "inventory.csv"}]

    # Mock the instance and its async method
    mock_retriever_instance = MagicMock()
    mock_retriever_instance.retrieve_context = AsyncMock(return_value=expected_context)
    mock_retriever_class.return_value = mock_retriever_instance

    # 2. Act
    # We call with only the query to test the default 'else' path
    result = await retrieve_context_with_metadata(query=mock_query)

    # 3. Assert
    assert result == expected_context
    mock_retriever_class.assert_called_once_with()
    
    # Check the method was called with *only* the query
    mock_retriever_instance.retrieve_context.assert_called_once_with(
        mock_query
    )

### test is_somewhat_uniform

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_dict", [
    {},             # Test case for len == 0
    {'a': 10}       # Test case for len == 1
])
async def test_is_somewhat_uniform_raises_assertion(invalid_dict):
    """
    Tests that the function raises an AssertionError if the dictionary
    contains fewer than two items.
    """
    # 1. Arrange (invalid_dict is from parametrize)
    
    # 2. Act & 3. Assert
    with pytest.raises(AssertionError, match="Frequency dictionary must contain more than one item."):
        await is_somewhat_uniform(invalid_dict)

# --- Tests for the Logic Branches ---

# We patch the threshold to a known value (0.5) for predictable tests.
# This ensures the test won't break if the real constant changes.
@pytest.mark.asyncio
@patch("src.logic.MODULE_PROPOSER_THRESHOLD", 0.8)
async def test_is_somewhat_uniform_all_zeros():
    """
    Tests the special case where all frequencies are 0.
    The mean is 0, and the function should return (True, 0).
    """
    # 1. Arrange
    test_dict = {'انبار': 0, 'دفتر کل': 0, 'خزانه داری': 0}
    expected_result = (True, 0.0)

    # 2. Act
    result = await is_somewhat_uniform(test_dict)

    # 3. Assert
    assert result == expected_result

@patch("src.logic.MODULE_PROPOSER_THRESHOLD", 0.8)
@pytest.mark.asyncio
async def test_is_somewhat_uniform_perfectly_uniform_passes():
    """
    Tests a perfectly uniform distribution (stdev=0, CV=0).
    CV (0.0) <= threshold (0.5) should return True.
    """
    # 1. Arrange
    test_dict = {'انبار': 10, 'دفتر کل': 10, 'خزانه داری': 10}
    # mean=10, stdev=0, cv=0
    expected_result = (True, 10.0)

    # 2. Act
    result = await is_somewhat_uniform(test_dict)

    # 3. Assert
    assert result[0] is True
    assert result[1] == pytest.approx(10.0) # Use approx for float comparison

@patch("src.logic.MODULE_PROPOSER_THRESHOLD", 0.8)
@pytest.mark.asyncio
async def test_is_somewhat_uniform_somewhat_uniform_passes():
    """
    Tests a slightly varied distribution that is still "uniform".
    CV (0.1) <= threshold (0.5) should return True.
    """
    # 1. Arrange
    test_dict = {'خزانه داری': 9, 'دفتر کل': 10, 'انبار': 11}
    # frequencies = [9, 10, 11]
    # mean = 10.0
    # stdev = 1.0
    # cv = 1.0 / 10.0 = 0.1
    expected_result = (True, 10.0)

    # 2. Act
    result = await is_somewhat_uniform(test_dict)

    # 3. Assert
    assert result[0] is True
    assert result[1] == pytest.approx(10.0) # Use approx for float comparison

@patch("src.logic.MODULE_PROPOSER_THRESHOLD", 0.8)
@pytest.mark.asyncio
async def test_is_somewhat_uniform_not_uniform_fails():
    """
    Tests a highly varied distribution that is "not uniform".
    CV (0.6546536707079771) < threshold (0.8) should return True.
    """
    # 1. Arrange
    test_dict = {'انبار': 4, 'دفتر کل': 2, 'خزانه داری': 1}
    
    expected_mean = 7/3
    expected_result = (False, expected_mean)

    # 2. Act
    result = await is_somewhat_uniform(test_dict_extreme)

    # 3. Assert
    assert result[0] is True
    assert result[1] == pytest.approx(expected_mean)

@patch("src.logic.MODULE_PROPOSER_THRESHOLD", 0.6)
@pytest.mark.asyncio
async def test_is_somewhat_uniform_not_uniform_fails():
    """
    Tests a highly varied distribution that is "not uniform".
    CV (0.6546536707079771) < threshold (0.6) should return False.
    """
    # 1. Arrange
    test_dict = {'انبار': 4, 'دفتر کل': 2, 'خزانه داری': 1}
    
    expected_mean = 7/3
    expected_result = (False, expected_mean)

    # 2. Act
    result = await is_somewhat_uniform(test_dict)

    # 3. Assert
    assert result[0] is True
    assert result[1] == pytest.approx(expected_mean)

@patch("src.logic.MODULE_PROPOSER_THRESHOLD", 0.5)
@pytest.mark.asyncio
async def test_is_somewhat_uniform_at_threshold_passes():
    """
    Tests a distribution where CV is exactly the threshold.
    CV (0.5) <= threshold (0.5) should return True.
    """
    # 1. Arrange
    test_dict = {'خزانه داری': 5, 'دفتر کل': 10, 'انبار': 15}
    
    expected_result = (True, 10.0)

    # 2. Act
    result = await is_somewhat_uniform(test_dict)

    # 3. Assert
    assert result[0] is True
    assert result[1] == pytest.approx(10.0)

### test prepare_final_context

@pytest.mark.asyncio
# We patch all dependencies, bottom-up
@patch("src.logic._handle_clarification_case")
@patch("src.logic._handle_clear_preference_case")
@patch("src.logic._handle_single_module_case")
@patch("src.logic.is_somewhat_uniform", new_callable=AsyncMock)
@patch("src.logic.retrieve_context_with_metadata", new_callable=AsyncMock)
async def test_prepare_final_context_no_context_found(
    mock_retrieve_context, 
    mock_is_uniform, 
    mock_handle_single, 
    mock_handle_clear, 
    mock_handle_clarify
):
    """
    Tests Path 1: retrieve_context_with_metadata returns an empty list.
    """
    # 1. Arrange
    mock_query = "چطوری سند تعریف کنم؟"
    mock_retrieve_context.return_value = []  # No context found
    expected_result = (False, [], [])

    # 2. Act
    result = await prepare_final_context(mock_query)

    # 3. Assert
    assert result == expected_result
    mock_retrieve_context.assert_called_once_with(mock_query, database_index=None, input_modules=None)
    # Ensure no other logic was triggered
    mock_is_uniform.assert_not_called()
    mock_handle_single.assert_not_called()
    mock_handle_clear.assert_not_called()
    mock_handle_clarify.assert_not_called()

@pytest.mark.asyncio
@patch("src.logic._handle_clarification_case")
@patch("src.logic._handle_clear_preference_case")
@patch("src.logic._handle_single_module_case")
@patch("src.logic.is_somewhat_uniform", new_callable=AsyncMock)
@patch("src.logic.retrieve_context_with_metadata", new_callable=AsyncMock)
async def test_prepare_final_context_with_input_module(
    mock_retrieve_context, 
    mock_is_uniform, 
    mock_handle_single, 
    mock_handle_clear, 
    mock_handle_clarify
):
    """
    Tests Path 2: An 'input_module' is provided, skipping detection.
    """
    # 1. Arrange
    mock_query = "test query"
    mock_db_index = "../VectorDB"
    mock_module ='دفتر کل'
    mock_context = [{"text": "# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه شرح های استاندارد\nشرح های استاندارد شرح هایی از سند هستند که اغلب تکرار می شوند و برای راحتی و تسریع انجام کار، تعریف می شوند.\nدر این بخش میتوانید با زدن کلید \" جدید\" چندین شرح استاندارد تعریف کنید.\nاین شرح ها در قلم سند حسابداری با انتخاب معین مربوطه به صورت سلکتور نمایش داده میشوند و شما میتوانید شرح دلخواه را انتخاب و در صورت نیاز تکمیل یا ویرایش کنید.\nشرح های استاندارد همواره قابل ویرایش هستند.\nپس از تکمیل اطلاعات، میتوانید حساب معین مورد نظر خود را ذخیره کنید.\n* امکان حذف یک حساب معین پس از استفاده وجود ندارد.\n* **راه اندازی اولیه:** با استفاده از این امکان از مسیر حسابداری مالی/ دفتر کل می‌توان در صورتیکه در سیستم ساختار حسابی تعریف نشده باشد، یک ساختار حساب ایجاد کرد.\nبرای اینکار در قسمت ساختار حساب‌ها و دفتر، گزینه ایجاد انتخاب می‌شود. یک ساختار حساب عمومی در سیستم ایجاد می‌گردد و با یک دفتری که ایجاد می‌شود، مرتبط می‌گردد. همچنین می‌توان با استفاده از گزینه دانلود، فایل ساختار حساب نمونه‌ای که ایجاد می‌شود را دانلود کرد و برای ایمپورت در سیستم استفاده کرد.\nنکته: راه اندازی اولیه به ازای هر شرکت انجام می شود.\n", "index": 12, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# تنظیمات دفتر کل\n## تنظیمات سند حسابداری\n### تنظیمات سایر ماژول ها\nبا فعال کردن این مورد، مجوز امکان ویرایش شماره فرعی و شرح سند در وضعیت بررسی به بعد برای اسناد صادر شده از دیگر ماژول ها وجود خواهد داشت.\nدر صورت انتخاب این بخش یک صفحه باز می‌شود که می‌توان به ازای هر دفتر، تیک فعال را انتخاب و سپس آن را اعمال کرد.\n", "index": 10, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# گزارش‎‌‌ها\n## گزارش تراز\n.\n* سال مالی: از طریق فیلتر سال مالی می توانید محدوده سال های مالی مورد نظر برای اجرای گزارش را تعیین نمایید.\n* نوع بازه زمانی: امکان تعیین بازه زمانی گزارش بر اساس دوره مالی یا تاریخ وجود دارد. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیق‌تر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\nنوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n* + افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند. پیش فرض همه انواع سند به جز اختتامیه و بستن حساب‌ها انتخاب شده است", "index": 29, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# گزارش‎‌‌ها\n## گزارش دفاتر\n. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیقتر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\n* نوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n+ افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند.\n* نوع حساب: میتوانید انتخاب کنید کدام انواع حساب ها در گزارش نمایش داده شوند که شامل موارد زیر هستند:\n* دائم\n* موقت\n* انتظامی\n* ویژگی حساب های معین: میتوانید انتخاب کنید که معین با کدام ویژگی نمایش داده شوند که شامل موارد زیر هستند", "index": 7, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# صدور سند حسابداری با ارز عملیاتی\n## اطلاعات سربرگ سند حسابداری\n* شعبه: لیست شعب فعال روی قفل شرکت که به آنها دسترسی داشته باشید، نمایش داده میشوند.\nدرصورتی که یک شعبه به عنوان شعبه پیش فرض کاربر انتخاب شده باشد، این شعبه در سند پر می‌شود و در صورت نیاز قابل تغییر است.\n* تاریخ: به صورت پیش فرض با تاریخ روز پر میشود. باید در محدوده سال مالی انتخابی و دوره مالی با وضعیت باز شده باشد.\n* نوع سند: برای اسناد صادر شده دستی در دفتر کل، با مقدار عمومی تکمیل شده است و قابل تغییر به انواع تعریف شده توسط کاربر است.\nبرای اسناد صادر شده از سایر ماژول ها، با نام ماژول صادر کننده سند تکمیل شده است .\n• امکان صدور سند با مقدار فیلد نوع سند افتتاحیه به صورت دستی تنها در اولین سال مالی وجود دارد.\n* شماره فرعی: شماره فرعی یک فیلد دستی و اختیاری است که شرکت ها میتوانند به دلایل مختلف مانند بایگانی یا ردیابی اسناد صادر شده، اقدام به ورود اطلاعات کنند. بر اساس تنظیمات سیستم میتوان یکتایی شماره فرعی را در سطح شرکت یا شعبه کنترل کرد. این کنترل برای همه اسناد از همه ماژول ها اعمال خواهد شد", "index": 9, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# قطعی کردن اسناد و صدور سند کل\n## صدور سند کل\nسند كل حاصل تجمیع سندهای قطعی صادرشده در سازمان، در یک بازه‌ی تاریخی مشخص است. سند كل معمولاً ماهانه صادر می‌شود. (برای دوره‌ی زمانی كوتاه‌تر از یک ماه و بیش از آن هم قابل صدور است). سازمانها بر اساس سند كل، دفتر روزنامه‌ی خود را كه یكی از دفاتر قانونی است تهیه می‌كنند.\nبرای صدور سند كل، ابتدا تمام اسناد حسابداری با وضعیت قطعی در محدوده‌ی تاریخی مشخص شده، بازیابی می‌شود. سپس مبالغ حساب‌های معین مربوط به هر حساب كل را به تفكیک مبلغ بدهكار/ بستانكار جمع كرده و نتیجه در حساب كل مربوطه نمایش داده می‌شود.\nبرای صدور سند کل از مسیر حسابداری مالی/ دفتر کل/ اسناد/ سند کل با انتخاب گزینه \"+\" به صفحه صدور سند کل می‌رویم. با انتخاب سند کل به فهرست اسناد کل می‌رویم و در آنجا نیز با انتخاب گزینه سند کل جدید، صفحه صدور سند کل را باز می‌کنیم.\nبر اساس تنظیمات کاربر، یعنی شرکت، دفتر و سال مالی باز می‌شود و قابل تغییر است. در صورتیکه این اطلاعات در پیش فرض مشخص نشده باشد، نیاز است توسط کاربر مشخص گردد.\nدر ابتدای صفحه توضیحات مربوط به دلیل صدور سند کل و الزامات آن آمده است. فیلتر های ذیل وجود دارد:\n* تاریخ / شماره سند: در این قسمت مشخص می شود که سند کل بر اساس تاریخ صادر شود یا شماره سند و پیش فرض بر اساس تاریخ است.\n* تاریخ: ابتدا و انتهای این تاریخ بر اساس کوچکترین و بزرگترین تاریخ اسناد قطعی شده نمایش داده می‌شود. تاریخ انتها قابل تغییر است.\n* روش صدور سند: در این قسمت روش صدور سند را از بین انواع کلی، روزانه، ماهانه و دوره‌ای قابل انتخاب است. پیش فرض ماهانه است. روش دوره‌ای بر اساس دوره‌های مالی تعریف در سال مالی صادر می‌شود.\n* صدور سند کل مجزا برای اسناد پایان سال: به صورت پیش فرض انتخاب شده است که به ازای اسناد پایان سال سندهای جداگانه صادر می‌شود.\nپس از مشخص کردن فیلتر های مورد نظر، گزینه صدور سند کل را انتخاب می‌کنیم و صفحه‌ای باز می‌شود که فرایند صدور را نمایش می‌دهد و در نهایت پس از اتمام عملیات پیام مناسب نمایش داده می‌شود.\n", "index": 3, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# معرفی دفتر\nبرای صدور سند حسابداری نیاز است دفتر در سیستم تعریف شود و ساختار حساب و ارز آن دفتر نیز مشخص گردد. برای اینکار از مسیر منوی اصلی/حسابداری مالی/ دفتر کل/ اطلاعات پایه/ دفتر را انتخاب می‌کنیم.\nفهرست دفترها باز می‌شود، با استفاده از گزینه جدید در بالا و سمت چپ صفحه به صفحه معرفی دفتر جدید می‌رویم.\nکد و عنوان دفتر را مشخص می‌کنیم، ساختار حساب را و ارز اصلی را انتخاب کرده و اگر این دفتر، دفتر اصلی سیستم است یعنی دفاتر قانونی شرکت با آن تهیه می‌شود، گزینه اصلی را انتخاب می‌کنیم.\nپس از آن صفحه ذخیره می‌شود.\nتصویر 1\n* در چند شرکتی دفتر در سطح گروه (مشترک) تعریف می‌شود و به شرکت‌ها گسترش داده می‌شود.\n", "index": 1, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه اطلاعات معین\n. در این فیلد میتوانید ماژول های مجاز به استفاده از معین مربوطه را مشخص کنید، بعد از انتخاب هر ماژول ، امکان انتخاب در فرم های استقرار حساب ماژول ها و صدور سند حسابداری با معین جاری در ماژول مورد نظر به کاربر داده می شود .\n* اگر بعد از استفاده ( در دفتر کل یا سایر ماژول ها ) امکان صدور سند از ماژول ها برداشته شود، در زمان صدور سند حسابداری از سمت همان ماژول کنترل می شود که معین های دارای این ویژگی استفاده شده باشند .\n* امکان مشاهده اطلاعات همه معین ها در گزارشات دفتر کل ( فارغ از اینکه امکان استفاده در دفتر کل برای آنها انتخاب شده باشد یا نه ) وجود دارد\n* **فعال:** وضعیت حساب معین را نمایش می دهد که می تواند فعال یا غیرفعال باشد.\nحساب معینی که گزینه \"فعال\" آن انتخاب نشده باشد، امکان شرکت در هیچ عملیاتی از جمله صدور سند حسابداری، نگاشت حساب ها، حساب های طرف مقابل، نخواهد داشت.\n* حساب های معین همواره امکان غیر فعال شدن دارند، در صورت فعال نبودن، در زمان صدور سند حسابداری های سیستمی اجازه صدور سند داده نمی‌شود", "index": 16, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# انوع سند حسابداری\nثبت کلیه رویدادهای مالی اعم از خرید و فروش، دریافت تسهیلات مالی، عملیات دریافت و پرداخت وجوه مالی و.... در قالب اسناد حسابداری انجام می‌شود؛ لذا متمایز بودن و امکان دسته بندی اسناد حسابدری حائز اهمیت خواهد بود تا بتوان جهت گزارشگری، بررسی و کنترل‌های داخلی از آن استفاده کرد. اين امكان در قالب انواع مختلف سند حسابداري در سیستم طراحی شده است و در هنگام ثبت اسناد حسابداري نوع آن به صورت دستی یا اتوماتیک مشخص می‌شود. انواع سند به چهار دسته کلی تقسیم می‌شوند:\n1. اسناد دستی صادر شده از دفتر کل که با نوع عمومی شناخته می‌شوند.\n2. اسناد سیستمی صادر شده از دفتر کل که شامل تسعیر ارز، عملیات پایان سال و .... می‌باشد.\n3. اسناد صادر شده از سایر ماژول‌ها ناشی از عملیات مرتبط با خرید، فروش انبار و غیره. نوع سند در این نوع از اسناد با توجه به ماژول مورد نظر به صورت خودکار ایجاد می‌شود. مانند: سند انبار، فروش، خزانه داری و ...\n4. اسناد دستی صادر شده از دفتر کل که کاربر نیاز دارد با نوع دلخواه خود جهت نیازمندی‌های گزارشگری تعریف کند", "index": 15, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# انوع سند حسابداری\n. ثبت می شود و با نوع ماژولی که از آن صادر می شوند، شناسایی می‌شوند. |\nدر صورتیکه کاربر نیاز داشته باشد یک نوع سند جدید در سیستم تعریف کند، از مسیر منو اصلی/ حسابداری مالی/ دفتر کل/ اسناد / نوع سند، کلید \"+\" را انتخاب می‎‌شود.\nتصویر 1\nبا انتخاب کلید\"+\" در نوع سند یک فرم به صورت \"تصویر 2\" باز می‌شود. عنوان مورد نظر مشخص می‌شود در صورت نیاز توضیحات نیز وارد می‌شود این مورد اجباری نیست سپس با انتخاب کلید ذخیره از گوشه سمت چپ و بالا، نوع سند ذخیره خواهد شد.\nتصویر 2\nانواع سندهای سیستمی شامل عمومی، عملیات پایان سال، بستن حساب‌ها و تسعیر ارز و ....، همچنین نوع سندهای مربوط به سایر ماژول‌ها توسط کاربران قابل ویرایش و حذف نیستد اما انواع سند ایجاد شده توسط کاربران، تا قبل از استفاده قابل حذف و ویرایش است. پس از استفاده نیز می‌توان با غیر فعال کردن نوع سند از استفاده آن جلوگیری کرد", "index": 2, "module": "دفتر کل", "source": "voucher.csv"}]
    
    mock_retrieve_context.return_value = mock_context
    mock_handle_single.return_value = [False, ["دفتر کل"], "# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه شرح های استاندارد\nشرح های استاندارد شرح هایی از سند هستند که اغلب تکرار می شوند و برای راحتی و تسریع انجام کار، تعریف می شوند.\nدر این بخش میتوانید با زدن کلید \" جدید\" چندین شرح استاندارد تعریف کنید.\nاین شرح ها در قلم سند حسابداری با انتخاب معین مربوطه به صورت سلکتور نمایش داده میشوند و شما میتوانید شرح دلخواه را انتخاب و در صورت نیاز تکمیل یا ویرایش کنید.\nشرح های استاندارد همواره قابل ویرایش هستند.\nپس از تکمیل اطلاعات، میتوانید حساب معین مورد نظر خود را ذخیره کنید.\n* امکان حذف یک حساب معین پس از استفاده وجود ندارد.\n* **راه اندازی اولیه:** با استفاده از این امکان از مسیر حسابداری مالی/ دفتر کل می‌توان در صورتیکه در سیستم ساختار حسابی تعریف نشده باشد، یک ساختار حساب ایجاد کرد.\nبرای اینکار در قسمت ساختار حساب‌ها و دفتر، گزینه ایجاد انتخاب می‌شود. یک ساختار حساب عمومی در سیستم ایجاد می‌گردد و با یک دفتری که ایجاد می‌شود، مرتبط می‌گردد. همچنین می‌توان با استفاده از گزینه دانلود، فایل ساختار حساب نمونه‌ای که ایجاد می‌شود را دانلود کرد و برای ایمپورت در سیستم استفاده کرد.\nنکته: راه اندازی اولیه به ازای هر شرکت انجام می شود.\n\n\n# تنظیمات دفتر کل\n## تنظیمات سند حسابداری\n### تنظیمات سایر ماژول ها\nبا فعال کردن این مورد، مجوز امکان ویرایش شماره فرعی و شرح سند در وضعیت بررسی به بعد برای اسناد صادر شده از دیگر ماژول ها وجود خواهد داشت.\nدر صورت انتخاب این بخش یک صفحه باز می‌شود که می‌توان به ازای هر دفتر، تیک فعال را انتخاب و سپس آن را اعمال کرد.\n\n\n# گزارش‎‌‌ها\n## گزارش تراز\n.\n* سال مالی: از طریق فیلتر سال مالی می توانید محدوده سال های مالی مورد نظر برای اجرای گزارش را تعیین نمایید.\n* نوع بازه زمانی: امکان تعیین بازه زمانی گزارش بر اساس دوره مالی یا تاریخ وجود دارد. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیق‌تر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\nنوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n* + افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند. پیش فرض همه انواع سند به جز اختتامیه و بستن حساب‌ها انتخاب شده است\n\n# گزارش‎‌‌ها\n## گزارش دفاتر\n. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیقتر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\n* نوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n+ افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند.\n* نوع حساب: میتوانید انتخاب کنید کدام انواع حساب ها در گزارش نمایش داده شوند که شامل موارد زیر هستند:\n* دائم\n* موقت\n* انتظامی\n* ویژگی حساب های معین: میتوانید انتخاب کنید که معین با کدام ویژگی نمایش داده شوند که شامل موارد زیر هستند\n\n# صدور سند حسابداری با ارز عملیاتی\n## اطلاعات سربرگ سند حسابداری\n* شعبه: لیست شعب فعال روی قفل شرکت که به آنها دسترسی داشته باشید، نمایش داده میشوند.\nدرصورتی که یک شعبه به عنوان شعبه پیش فرض کاربر انتخاب شده باشد، این شعبه در سند پر می‌شود و در صورت نیاز قابل تغییر است.\n* تاریخ: به صورت پیش فرض با تاریخ روز پر میشود. باید در محدوده سال مالی انتخابی و دوره مالی با وضعیت باز شده باشد.\n* نوع سند: برای اسناد صادر شده دستی در دفتر کل، با مقدار عمومی تکمیل شده است و قابل تغییر به انواع تعریف شده توسط کاربر است.\nبرای اسناد صادر شده از سایر ماژول ها، با نام ماژول صادر کننده سند تکمیل شده است .\n• امکان صدور سند با مقدار فیلد نوع سند افتتاحیه به صورت دستی تنها در اولین سال مالی وجود دارد.\n* شماره فرعی: شماره فرعی یک فیلد دستی و اختیاری است که شرکت ها میتوانند به دلایل مختلف مانند بایگانی یا ردیابی اسناد صادر شده، اقدام به ورود اطلاعات کنند. بر اساس تنظیمات سیستم میتوان یکتایی شماره فرعی را در سطح شرکت یا شعبه کنترل کرد. این کنترل برای همه اسناد از همه ماژول ها اعمال خواهد شد\n\n# قطعی کردن اسناد و صدور سند کل\n## صدور سند کل\nسند كل حاصل تجمیع سندهای قطعی صادرشده در سازمان، در یک بازه‌ی تاریخی مشخص است. سند كل معمولاً ماهانه صادر می‌شود. (برای دوره‌ی زمانی كوتاه‌تر از یک ماه و بیش از آن هم قابل صدور است). سازمانها بر اساس سند كل، دفتر روزنامه‌ی خود را كه یكی از دفاتر قانونی است تهیه می‌كنند.\nبرای صدور سند كل، ابتدا تمام اسناد حسابداری با وضعیت قطعی در محدوده‌ی تاریخی مشخص شده، بازیابی می‌شود. سپس مبالغ حساب‌های معین مربوط به هر حساب كل را به تفكیک مبلغ بدهكار/ بستانكار جمع كرده و نتیجه در حساب كل مربوطه نمایش داده می‌شود.\nبرای صدور سند کل از مسیر حسابداری مالی/ دفتر کل/ اسناد/ سند کل با انتخاب گزینه \"+\" به صفحه صدور سند کل می‌رویم. با انتخاب سند کل به فهرست اسناد کل می‌رویم و در آنجا نیز با انتخاب گزینه سند کل جدید، صفحه صدور سند کل را باز می‌کنیم.\nبر اساس تنظیمات کاربر، یعنی شرکت، دفتر و سال مالی باز می‌شود و قابل تغییر است. در صورتیکه این اطلاعات در پیش فرض مشخص نشده باشد، نیاز است توسط کاربر مشخص گردد.\nدر ابتدای صفحه توضیحات مربوط به دلیل صدور سند کل و الزامات آن آمده است. فیلتر های ذیل وجود دارد:\n* تاریخ / شماره سند: در این قسمت مشخص می شود که سند کل بر اساس تاریخ صادر شود یا شماره سند و پیش فرض بر اساس تاریخ است.\n* تاریخ: ابتدا و انتهای این تاریخ بر اساس کوچکترین و بزرگترین تاریخ اسناد قطعی شده نمایش داده می‌شود. تاریخ انتها قابل تغییر است.\n* روش صدور سند: در این قسمت روش صدور سند را از بین انواع کلی، روزانه، ماهانه و دوره‌ای قابل انتخاب است. پیش فرض ماهانه است. روش دوره‌ای بر اساس دوره‌های مالی تعریف در سال مالی صادر می‌شود.\n* صدور سند کل مجزا برای اسناد پایان سال: به صورت پیش فرض انتخاب شده است که به ازای اسناد پایان سال سندهای جداگانه صادر می‌شود.\nپس از مشخص کردن فیلتر های مورد نظر، گزینه صدور سند کل را انتخاب می‌کنیم و صفحه‌ای باز می‌شود که فرایند صدور را نمایش می‌دهد و در نهایت پس از اتمام عملیات پیام مناسب نمایش داده می‌شود.\n\n\n# معرفی دفتر\nبرای صدور سند حسابداری نیاز است دفتر در سیستم تعریف شود و ساختار حساب و ارز آن دفتر نیز مشخص گردد. برای اینکار از مسیر منوی اصلی/حسابداری مالی/ دفتر کل/ اطلاعات پایه/ دفتر را انتخاب می‌کنیم.\nفهرست دفترها باز می‌شود، با استفاده از گزینه جدید در بالا و سمت چپ صفحه به صفحه معرفی دفتر جدید می‌رویم.\nکد و عنوان دفتر را مشخص می‌کنیم، ساختار حساب را و ارز اصلی را انتخاب کرده و اگر این دفتر، دفتر اصلی سیستم است یعنی دفاتر قانونی شرکت با آن تهیه می‌شود، گزینه اصلی را انتخاب می‌کنیم.\nپس از آن صفحه ذخیره می‌شود.\nتصویر 1\n* در چند شرکتی دفتر در سطح گروه (مشترک) تعریف می‌شود و به شرکت‌ها گسترش داده می‌شود.\n\n\n# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه اطلاعات معین\n. در این فیلد میتوانید ماژول های مجاز به استفاده از معین مربوطه را مشخص کنید، بعد از انتخاب هر ماژول ، امکان انتخاب در فرم های استقرار حساب ماژول ها و صدور سند حسابداری با معین جاری در ماژول مورد نظر به کاربر داده می شود .\n* اگر بعد از استفاده ( در دفتر کل یا سایر ماژول ها ) امکان صدور سند از ماژول ها برداشته شود، در زمان صدور سند حسابداری از سمت همان ماژول کنترل می شود که معین های دارای این ویژگی استفاده شده باشند .\n* امکان مشاهده اطلاعات همه معین ها در گزارشات دفتر کل ( فارغ از اینکه امکان استفاده در دفتر کل برای آنها انتخاب شده باشد یا نه ) وجود دارد\n* **فعال:** وضعیت حساب معین را نمایش می دهد که می تواند فعال یا غیرفعال باشد.\nحساب معینی که گزینه \"فعال\" آن انتخاب نشده باشد، امکان شرکت در هیچ عملیاتی از جمله صدور سند حسابداری، نگاشت حساب ها، حساب های طرف مقابل، نخواهد داشت.\n* حساب های معین همواره امکان غیر فعال شدن دارند، در صورت فعال نبودن، در زمان صدور سند حسابداری های سیستمی اجازه صدور سند داده نمی‌شود\n\n# انوع سند حسابداری\nثبت کلیه رویدادهای مالی اعم از خرید و فروش، دریافت تسهیلات مالی، عملیات دریافت و پرداخت وجوه مالی و.... در قالب اسناد حسابداری انجام می‌شود؛ لذا متمایز بودن و امکان دسته بندی اسناد حسابدری حائز اهمیت خواهد بود تا بتوان جهت گزارشگری، بررسی و کنترل‌های داخلی از آن استفاده کرد. اين امكان در قالب انواع مختلف سند حسابداري در سیستم طراحی شده است و در هنگام ثبت اسناد حسابداري نوع آن به صورت دستی یا اتوماتیک مشخص می‌شود. انواع سند به چهار دسته کلی تقسیم می‌شوند:\n1. اسناد دستی صادر شده از دفتر کل که با نوع عمومی شناخته می‌شوند.\n2. اسناد سیستمی صادر شده از دفتر کل که شامل تسعیر ارز، عملیات پایان سال و .... می‌باشد.\n3. اسناد صادر شده از سایر ماژول‌ها ناشی از عملیات مرتبط با خرید، فروش انبار و غیره. نوع سند در این نوع از اسناد با توجه به ماژول مورد نظر به صورت خودکار ایجاد می‌شود. مانند: سند انبار، فروش، خزانه داری و ...\n4. اسناد دستی صادر شده از دفتر کل که کاربر نیاز دارد با نوع دلخواه خود جهت نیازمندی‌های گزارشگری تعریف کند\n\n# انوع سند حسابداری\n. ثبت می شود و با نوع ماژولی که از آن صادر می شوند، شناسایی می‌شوند. |\nدر صورتیکه کاربر نیاز داشته باشد یک نوع سند جدید در سیستم تعریف کند، از مسیر منو اصلی/ حسابداری مالی/ دفتر کل/ اسناد / نوع سند، کلید \"+\" را انتخاب می‎‌شود.\nتصویر 1\nبا انتخاب کلید\"+\" در نوع سند یک فرم به صورت \"تصویر 2\" باز می‌شود. عنوان مورد نظر مشخص می‌شود در صورت نیاز توضیحات نیز وارد می‌شود این مورد اجباری نیست سپس با انتخاب کلید ذخیره از گوشه سمت چپ و بالا، نوع سند ذخیره خواهد شد.\nتصویر 2\nانواع سندهای سیستمی شامل عمومی، عملیات پایان سال، بستن حساب‌ها و تسعیر ارز و ....، همچنین نوع سندهای مربوط به سایر ماژول‌ها توسط کاربران قابل ویرایش و حذف نیستد اما انواع سند ایجاد شده توسط کاربران، تا قبل از استفاده قابل حذف و ویرایش است. پس از استفاده نیز می‌توان با غیر فعال کردن نوع سند از استفاده آن جلوگیری کرد"]

    # 2. Act
    result = await prepare_final_context(mock_query, input_module=mock_module)

    # 3. Assert
    assert result == [False, ["دفتر کل"], "# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه شرح های استاندارد\nشرح های استاندارد شرح هایی از سند هستند که اغلب تکرار می شوند و برای راحتی و تسریع انجام کار، تعریف می شوند.\nدر این بخش میتوانید با زدن کلید \" جدید\" چندین شرح استاندارد تعریف کنید.\nاین شرح ها در قلم سند حسابداری با انتخاب معین مربوطه به صورت سلکتور نمایش داده میشوند و شما میتوانید شرح دلخواه را انتخاب و در صورت نیاز تکمیل یا ویرایش کنید.\nشرح های استاندارد همواره قابل ویرایش هستند.\nپس از تکمیل اطلاعات، میتوانید حساب معین مورد نظر خود را ذخیره کنید.\n* امکان حذف یک حساب معین پس از استفاده وجود ندارد.\n* **راه اندازی اولیه:** با استفاده از این امکان از مسیر حسابداری مالی/ دفتر کل می‌توان در صورتیکه در سیستم ساختار حسابی تعریف نشده باشد، یک ساختار حساب ایجاد کرد.\nبرای اینکار در قسمت ساختار حساب‌ها و دفتر، گزینه ایجاد انتخاب می‌شود. یک ساختار حساب عمومی در سیستم ایجاد می‌گردد و با یک دفتری که ایجاد می‌شود، مرتبط می‌گردد. همچنین می‌توان با استفاده از گزینه دانلود، فایل ساختار حساب نمونه‌ای که ایجاد می‌شود را دانلود کرد و برای ایمپورت در سیستم استفاده کرد.\nنکته: راه اندازی اولیه به ازای هر شرکت انجام می شود.\n\n\n# تنظیمات دفتر کل\n## تنظیمات سند حسابداری\n### تنظیمات سایر ماژول ها\nبا فعال کردن این مورد، مجوز امکان ویرایش شماره فرعی و شرح سند در وضعیت بررسی به بعد برای اسناد صادر شده از دیگر ماژول ها وجود خواهد داشت.\nدر صورت انتخاب این بخش یک صفحه باز می‌شود که می‌توان به ازای هر دفتر، تیک فعال را انتخاب و سپس آن را اعمال کرد.\n\n\n# گزارش‎‌‌ها\n## گزارش تراز\n.\n* سال مالی: از طریق فیلتر سال مالی می توانید محدوده سال های مالی مورد نظر برای اجرای گزارش را تعیین نمایید.\n* نوع بازه زمانی: امکان تعیین بازه زمانی گزارش بر اساس دوره مالی یا تاریخ وجود دارد. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیق‌تر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\nنوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n* + افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند. پیش فرض همه انواع سند به جز اختتامیه و بستن حساب‌ها انتخاب شده است\n\n# گزارش‎‌‌ها\n## گزارش دفاتر\n. در صورت انتخاب دوره مالی، می توان دوره های مالی را فیلتر نمود. همچنین در صورت انتخاب تاریخ، می توان محدوده دقیقتر گزارش بر اساس تاریخ اسناد را تعیین کرد.\n* دوره مالی: طبق دوره های تعریف شده در فرم سال مالی دوره های مربوط به سال های مالی انتخاب شده در فیلتر سال مالی نمایش داده میشوند و امکان تعیین محدوده مورد نظر برای دوره های مالی را دارید.\n* نوع سند: انواع سند تعریف شده در سیستم قابل انتخاب و فیلتر کردن است. انواع سند شامل موارد زیر است:\n+ افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند.\n* نوع حساب: میتوانید انتخاب کنید کدام انواع حساب ها در گزارش نمایش داده شوند که شامل موارد زیر هستند:\n* دائم\n* موقت\n* انتظامی\n* ویژگی حساب های معین: میتوانید انتخاب کنید که معین با کدام ویژگی نمایش داده شوند که شامل موارد زیر هستند\n\n# صدور سند حسابداری با ارز عملیاتی\n## اطلاعات سربرگ سند حسابداری\n* شعبه: لیست شعب فعال روی قفل شرکت که به آنها دسترسی داشته باشید، نمایش داده میشوند.\nدرصورتی که یک شعبه به عنوان شعبه پیش فرض کاربر انتخاب شده باشد، این شعبه در سند پر می‌شود و در صورت نیاز قابل تغییر است.\n* تاریخ: به صورت پیش فرض با تاریخ روز پر میشود. باید در محدوده سال مالی انتخابی و دوره مالی با وضعیت باز شده باشد.\n* نوع سند: برای اسناد صادر شده دستی در دفتر کل، با مقدار عمومی تکمیل شده است و قابل تغییر به انواع تعریف شده توسط کاربر است.\nبرای اسناد صادر شده از سایر ماژول ها، با نام ماژول صادر کننده سند تکمیل شده است .\n• امکان صدور سند با مقدار فیلد نوع سند افتتاحیه به صورت دستی تنها در اولین سال مالی وجود دارد.\n* شماره فرعی: شماره فرعی یک فیلد دستی و اختیاری است که شرکت ها میتوانند به دلایل مختلف مانند بایگانی یا ردیابی اسناد صادر شده، اقدام به ورود اطلاعات کنند. بر اساس تنظیمات سیستم میتوان یکتایی شماره فرعی را در سطح شرکت یا شعبه کنترل کرد. این کنترل برای همه اسناد از همه ماژول ها اعمال خواهد شد\n\n# قطعی کردن اسناد و صدور سند کل\n## صدور سند کل\nسند كل حاصل تجمیع سندهای قطعی صادرشده در سازمان، در یک بازه‌ی تاریخی مشخص است. سند كل معمولاً ماهانه صادر می‌شود. (برای دوره‌ی زمانی كوتاه‌تر از یک ماه و بیش از آن هم قابل صدور است). سازمانها بر اساس سند كل، دفتر روزنامه‌ی خود را كه یكی از دفاتر قانونی است تهیه می‌كنند.\nبرای صدور سند كل، ابتدا تمام اسناد حسابداری با وضعیت قطعی در محدوده‌ی تاریخی مشخص شده، بازیابی می‌شود. سپس مبالغ حساب‌های معین مربوط به هر حساب كل را به تفكیک مبلغ بدهكار/ بستانكار جمع كرده و نتیجه در حساب كل مربوطه نمایش داده می‌شود.\nبرای صدور سند کل از مسیر حسابداری مالی/ دفتر کل/ اسناد/ سند کل با انتخاب گزینه \"+\" به صفحه صدور سند کل می‌رویم. با انتخاب سند کل به فهرست اسناد کل می‌رویم و در آنجا نیز با انتخاب گزینه سند کل جدید، صفحه صدور سند کل را باز می‌کنیم.\nبر اساس تنظیمات کاربر، یعنی شرکت، دفتر و سال مالی باز می‌شود و قابل تغییر است. در صورتیکه این اطلاعات در پیش فرض مشخص نشده باشد، نیاز است توسط کاربر مشخص گردد.\nدر ابتدای صفحه توضیحات مربوط به دلیل صدور سند کل و الزامات آن آمده است. فیلتر های ذیل وجود دارد:\n* تاریخ / شماره سند: در این قسمت مشخص می شود که سند کل بر اساس تاریخ صادر شود یا شماره سند و پیش فرض بر اساس تاریخ است.\n* تاریخ: ابتدا و انتهای این تاریخ بر اساس کوچکترین و بزرگترین تاریخ اسناد قطعی شده نمایش داده می‌شود. تاریخ انتها قابل تغییر است.\n* روش صدور سند: در این قسمت روش صدور سند را از بین انواع کلی، روزانه، ماهانه و دوره‌ای قابل انتخاب است. پیش فرض ماهانه است. روش دوره‌ای بر اساس دوره‌های مالی تعریف در سال مالی صادر می‌شود.\n* صدور سند کل مجزا برای اسناد پایان سال: به صورت پیش فرض انتخاب شده است که به ازای اسناد پایان سال سندهای جداگانه صادر می‌شود.\nپس از مشخص کردن فیلتر های مورد نظر، گزینه صدور سند کل را انتخاب می‌کنیم و صفحه‌ای باز می‌شود که فرایند صدور را نمایش می‌دهد و در نهایت پس از اتمام عملیات پیام مناسب نمایش داده می‌شود.\n\n\n# معرفی دفتر\nبرای صدور سند حسابداری نیاز است دفتر در سیستم تعریف شود و ساختار حساب و ارز آن دفتر نیز مشخص گردد. برای اینکار از مسیر منوی اصلی/حسابداری مالی/ دفتر کل/ اطلاعات پایه/ دفتر را انتخاب می‌کنیم.\nفهرست دفترها باز می‌شود، با استفاده از گزینه جدید در بالا و سمت چپ صفحه به صفحه معرفی دفتر جدید می‌رویم.\nکد و عنوان دفتر را مشخص می‌کنیم، ساختار حساب را و ارز اصلی را انتخاب کرده و اگر این دفتر، دفتر اصلی سیستم است یعنی دفاتر قانونی شرکت با آن تهیه می‌شود، گزینه اصلی را انتخاب می‌کنیم.\nپس از آن صفحه ذخیره می‌شود.\nتصویر 1\n* در چند شرکتی دفتر در سطح گروه (مشترک) تعریف می‌شود و به شرکت‌ها گسترش داده می‌شود.\n\n\n# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه اطلاعات معین\n. در این فیلد میتوانید ماژول های مجاز به استفاده از معین مربوطه را مشخص کنید، بعد از انتخاب هر ماژول ، امکان انتخاب در فرم های استقرار حساب ماژول ها و صدور سند حسابداری با معین جاری در ماژول مورد نظر به کاربر داده می شود .\n* اگر بعد از استفاده ( در دفتر کل یا سایر ماژول ها ) امکان صدور سند از ماژول ها برداشته شود، در زمان صدور سند حسابداری از سمت همان ماژول کنترل می شود که معین های دارای این ویژگی استفاده شده باشند .\n* امکان مشاهده اطلاعات همه معین ها در گزارشات دفتر کل ( فارغ از اینکه امکان استفاده در دفتر کل برای آنها انتخاب شده باشد یا نه ) وجود دارد\n* **فعال:** وضعیت حساب معین را نمایش می دهد که می تواند فعال یا غیرفعال باشد.\nحساب معینی که گزینه \"فعال\" آن انتخاب نشده باشد، امکان شرکت در هیچ عملیاتی از جمله صدور سند حسابداری، نگاشت حساب ها، حساب های طرف مقابل، نخواهد داشت.\n* حساب های معین همواره امکان غیر فعال شدن دارند، در صورت فعال نبودن، در زمان صدور سند حسابداری های سیستمی اجازه صدور سند داده نمی‌شود\n\n# انوع سند حسابداری\nثبت کلیه رویدادهای مالی اعم از خرید و فروش، دریافت تسهیلات مالی، عملیات دریافت و پرداخت وجوه مالی و.... در قالب اسناد حسابداری انجام می‌شود؛ لذا متمایز بودن و امکان دسته بندی اسناد حسابدری حائز اهمیت خواهد بود تا بتوان جهت گزارشگری، بررسی و کنترل‌های داخلی از آن استفاده کرد. اين امكان در قالب انواع مختلف سند حسابداري در سیستم طراحی شده است و در هنگام ثبت اسناد حسابداري نوع آن به صورت دستی یا اتوماتیک مشخص می‌شود. انواع سند به چهار دسته کلی تقسیم می‌شوند:\n1. اسناد دستی صادر شده از دفتر کل که با نوع عمومی شناخته می‌شوند.\n2. اسناد سیستمی صادر شده از دفتر کل که شامل تسعیر ارز، عملیات پایان سال و .... می‌باشد.\n3. اسناد صادر شده از سایر ماژول‌ها ناشی از عملیات مرتبط با خرید، فروش انبار و غیره. نوع سند در این نوع از اسناد با توجه به ماژول مورد نظر به صورت خودکار ایجاد می‌شود. مانند: سند انبار، فروش، خزانه داری و ...\n4. اسناد دستی صادر شده از دفتر کل که کاربر نیاز دارد با نوع دلخواه خود جهت نیازمندی‌های گزارشگری تعریف کند\n\n# انوع سند حسابداری\n. ثبت می شود و با نوع ماژولی که از آن صادر می شوند، شناسایی می‌شوند. |\nدر صورتیکه کاربر نیاز داشته باشد یک نوع سند جدید در سیستم تعریف کند، از مسیر منو اصلی/ حسابداری مالی/ دفتر کل/ اسناد / نوع سند، کلید \"+\" را انتخاب می‎‌شود.\nتصویر 1\nبا انتخاب کلید\"+\" در نوع سند یک فرم به صورت \"تصویر 2\" باز می‌شود. عنوان مورد نظر مشخص می‌شود در صورت نیاز توضیحات نیز وارد می‌شود این مورد اجباری نیست سپس با انتخاب کلید ذخیره از گوشه سمت چپ و بالا، نوع سند ذخیره خواهد شد.\nتصویر 2\nانواع سندهای سیستمی شامل عمومی، عملیات پایان سال، بستن حساب‌ها و تسعیر ارز و ....، همچنین نوع سندهای مربوط به سایر ماژول‌ها توسط کاربران قابل ویرایش و حذف نیستد اما انواع سند ایجاد شده توسط کاربران، تا قبل از استفاده قابل حذف و ویرایش است. پس از استفاده نیز می‌توان با غیر فعال کردن نوع سند از استفاده آن جلوگیری کرد"]
    mock_retrieve_context.assert_called_once_with(
        mock_query, 
        database_index=None, 
        input_modules=[mock_module]
    )
    mock_handle_single.assert_called_once_with(mock_context, mock_module)
    # Ensure detection logic was skipped
    mock_is_uniform.assert_not_called()
    mock_handle_clear.assert_not_called()
    mock_handle_clarify.assert_not_called()

@pytest.mark.asyncio
@patch("src.logic._handle_clarification_case")
@patch("src.logic._handle_clear_preference_case")
@patch("src.logic._handle_single_module_case")
@patch("src.logic.is_somewhat_uniform", new_callable=AsyncMock)
@patch("src.logic.retrieve_context_with_metadata", new_callable=AsyncMock)
async def test_prepare_final_context_one_module_detected(
    mock_retrieve_context, 
    mock_is_uniform, 
    mock_handle_single, 
    mock_handle_clear, 
    mock_handle_clarify
):
    """
    Tests Path 3: No input_module, but detection finds only one module.
    (len(module_frequencies) < 2)
    """
    # 1. Arrange
    mock_db_index='../VectorDB'
    mock_query = 'چطوری سند انبار تعریف کنم؟'
    mock_context = [{"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n.\n* طرف مقابل در اسناد دریافت از تولید پروژه، برگشت دریافت از تولید پروژه، ارسال به تولید پروژه، برگشت ارسال به تولید پروژه، مصرف پروژه، برگشت مصرف پروژه، برگشت مصرف پروژه، تحویل دارایی ثابت به پروژه، برگشت تحویل دارایی ثابت به پروژه، ارسال ضایعات پروژه، برگشت ارسال ضایعات پروژه، دریافت ضایعات پروژه، **پروژه** می باشد.\n* طرف مقابل در اسناد تحویل فروش، برگشت تحویل فروش، **مشتری** می باشد.\n* طرف مقابل در اسناد دریافت امانی دیگران نزد ما، برگشت دریافت امانی دیگران نزد ما، ارسال امانی ما به دیگران، برگشت ارسال امانی ما به دیگران، شخص/شرکت **طرف حساب امانی** می باشد.\n* طرف مقابل در اسناد رسید دائم سایر، حواله دائم سایر، رسید ضایعات سایر، حواله ضایعات سایر، **شخص/شرکت با کلیه ی نقش های مشتری، تأمین کننده، کارمند، پیمانکار، تنخواه دار، صندوقدار، حمل کننده، کارمند فروش، طرف حساب امانی و سایر نقش ها** می باشد.\n* در اسناد رسید و حواله انتقال بین انبار، به جای فیلد طرف مقابل، **انبار مقابل** را خواهیم داشت که لیستی از **انبارها** را نمایش می دهد", "index": 7, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: مرکز هزینه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا\nویژگی های الگوی سند انبار برگشت تحویل دارایی ثابت به مرکز عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: مرکز هزینه (غیرقابل تغییر)\n* الگوی سند عطف: تحویل دارایی ثابت به مرکز (غیرقابل تغییر)\nویژگی های الگوی سند انبار تحویل دارایی ثابت به پروژه عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا\nویژگی های الگوی سند انبار برگشت تحویل دارایی ثابت به پروژه عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا", "index": 18, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n.\n* اطلاعات تکمیلی دریافت ضایعات مرکز شامل شماره دستور تولید، شماره سفارش تولید، شماره عملیات تولید، شیفت تولید و تاریخ تولید می باشد.\n* اطلاعات تکمیلی دریافت ضایعات پروژه شامل شماره دستور تولید، شماره سفارش تولید، شماره عملیات تولید، شیفت تولید و تاریخ تولید می باشد.\n* اطلاعات تکمیلی حواله انتقال بین انبار شامل شماره بازرسی کیفیت، شماره چک لیست، شماره آزمایشگاه، تایید ارفاقی، نتیجه بازرسی، نام راننده، نام خودرو، شماره پلاک، شماره بارنامه، تاریخ بارنامه و تلفن راننده می باشد.\n* اطلاعات تکمیلی حواله انتقال بین انبار شامل شماره بازرسی کیفیت، شماره چک لیست، شماره آزمایشگاه، تایید ارفاقی، نتیجه بازرسی، نام راننده، نام خودرو، شماره پلاک، شماره بارنامه، تاریخ بارنامه و تلفن راننده می باشد.\n* اطلاعات تکمیلی تحویل فروش شامل شماره سفارش فروش، شماره فاکتور فروش، مرکز فروش، فروشگاه، تحویل دهنده، شماره برگه باسکول، نام راننده، نام خودرو، شماره پلاک، شماره بارنامه، تاریخ بارنامه و تلفن راننده می باشد", "index": 19, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: طرف حساب امانی (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت دریافت امانی دیگران نزد ما عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: طرف حساب امانی (غیرقابل تغییر)\n* الگوی سند عطف: دریافت امانی دیگران نزد ما (غیرقابل تغییر)\nویژگی های الگوی سند انبار ارسال امانی ما به دیگران عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: طرف حساب امانی (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت ارسال امانی ما به دیگران عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)", "index": 1, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* سند مبنا: درخواست کالا (غیرقابل تغییر)\nویژگی های الگوی سند انبار رسید انتقال بین انبار عبارت است از:\n* نوع سند: انتقال بین انبار (غیرقابل تغییر)\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* الگوی سند عطف: حواله انتقال بین انبار (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت ارسال ضایعات مرکز عبارت است از:\n* نوع سند: ضایعات (غیرقابل تغییر)\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: مشتری (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت تحویل فروش عبارت است از:\n* نوع سند: فروش (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: مشتری (غیرقابل تغییر)\n* مبناها: سفارش فروش، فاکتور فروش\nویژگی های الگوی سند انبار دریافت امانی دیگران نزد ما عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)", "index": 14, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: مرکز هزینه (غیرقابل تغییر)\n* الگوی سند عطف: مصرف مرکز (غیرقابل تغییر)\nویژگی های الگوی سند انبار مصرف پروژه عبارت است از:\n* نوع سند: مصرف (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا\nویژگی های الگوی سند انبار برگشت مصرف پروژه عبارت است از:\n* نوع سند: مصرف (غیرقابل تغییر)\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* الگوی سند عطف: مصرف پروژه (غیرقابل تغییر)\nویژگی های الگوی سند انبار تحویل دارایی ثابت به مرکز عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)", "index": 13, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### فهرست سند انبار\nدر صفحه ی فهرست سند انبار می توان لیستی از اسناد انبار تعریف شده در سیستم را مشاهده کرد. ستون های قابل نمایش در فهرست سند انبار عبارتند از شماره سند، الگوی سند، نوع سند، انبار، تاریخ، وضعیت سند، وضعیت قیمت گذاری، وضعیت سند حسابداری و توضیحات.\nبرای مشاهده­ی لیست سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست سند انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2", "index": 36, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\nدر سیستم انبار، **برای ثبت گردش کالا از ثبت سند استفاده می شود. با توجه به رویدادی که در واقعیت اتفاق می افتند انباردار از الگوی سند مناسب آن استفاده می کند. از آنجایی که برای ثبت سند انبار هر شرکت می تواند علاوه بر اطلاعات اجباری هر سند، اطلاعات دیگری را به منظور استفاده در گزارش ها و فرایندهای انبار استفاده نماید، در الگوی سند انبار می توان آنها را تعریف و تنظیم نمود.** **در این بخش اسناد انبار به همراه همه فیلدهای استاندارد موجود در سیستم آمده است.**\nبرای ثبت سند انبار ابتدا لازم است شرکت و الگوی مناسب برای ثبت سند انتخاب شود. در صورتی که الگو و شرکت انتخابی برای کاربر، جز موارد پرکاربرد برای کاربر است، کاربر می تواند افزودن به منو را انتخاب کرده و در این حالت یک منو با عنوان الگوهای سند منتخب به منو اضافه شده و در زیر آن الگوی انتخابی اضافه می گردد.\nاز فرم الگوهای اسناد انبار به منظور تنظیم الگوهای مورد هر نیاز استفاده می شود. الگوهای استاندارد در انبار بر اساس کارکردهای یک انبار عمومی شناسایی شده و در سیستم قرار گرفته است. در ابتدای شروع به کار سیستم نیاز است، از استقرار الگوی سند انبار به منظور ایجاد الگوهای استاندارد استفاده می شود. الگوهای سند انبار دارای بخش های اطلاعات اصلی، سایر طرف مقابل ها، اطلاعات تکمیلی و فیلدهای اضافه می باشد.\n\n### فهرست الگوی سند انبار\n### مراحل تعریف الگوی سند انبار", "index": 28, "module": "انبار", "source": "inventory.csv"}, {"text": "# انبار\n### مراحل تعریف انبار\nبرای تعریف انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، اطلاعات پایه، انبار، گزینه معرفی انبار (+) را انتخاب نمایید.\nبرای معرفی انبار در منوی لجستیک ابتدا کد و عنوان انبار را تعریف کرده سپس مرکز نگهداری و نوع انبار را به آن اختصاص می دهیم. در پایان نیز در قسمت الگوهای مرتبط، الگوهای سند مجاز برای استفاده در این انبار را انتخاب می کنیم.\nگزینه های بالای صفحه ی ایجاد انبار جدید به شرح زیر می باشد:\n1. نام شرکت: شرکتی را که در آن انبار ایجاد می کنیم نمایش می دهد.\n2. ذخیره: این گزینه امکان \"ذخیره\" و “ذخیره و جدید” انبار جدید را فراهم می کند.\n3. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم معرفی انبار را فراهم می کند.\n4. سایر عملیات: این گزینه امکان ایجاد انبار جدید و نمایش فهرست انبار را فراهم می سازد.\n", "index": 35, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\nبرای تعریف الگوی سند انبار از الگوی ثبت سند انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای تعریف الگوی سند انبار ابتدا لازم است از فهرست الگوهای استاندارد یکی از الگوها انتخاب شده و وارد فرم مشاهده و ویرایش آن شود.\nدر مشاهده الگوهای سند انبار 4 بخش زیر وجود دارد\n1. اطلاعات اصلی\n2. سایر طرف مقابل ها\n3. اطلاعات تکمیلی\n4. فیلدهای اضافه\nدر بخش اطلاعات اصلی فیلدهای زیر تکمیل می گردد:\n1. کد الگو که غیرقابل ویرایش است.\n2. عنوان الگو که عنوان پیشفرض نمایش داده شده و کاربر می تواند عنوان مورد نظر خود را وارد نماید.\n3. فیلدهای نوع سند، جهت سند، نوع خرید (در اسناد خرید) و نوع تاثیر بر موجودی غیرقابل تغییر بوده و در الگوها قرار گرفته است.\n4. تعداد اقلام سند، تعداد مجاز ردیف های سند انبار است که به صورت پیشفرض 200 ردیف بوده و حداکثر میتواند 500 رکورد باشد.\n5. فیلدهای اجباری و ویرایش درقلم می تواند برای طرف مقابل برای استفاده از امکان تغییر طرف مقابل در اقلام سند انبار استفاده شود.\n6", "index": 11, "module": "انبار", "source": "inventory.csv"}]
    
    mock_retrieve_context.return_value = mock_context
    mock_handle_single.return_value = [False, ["انبار"], "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n.\n* طرف مقابل در اسناد دریافت از تولید پروژه، برگشت دریافت از تولید پروژه، ارسال به تولید پروژه، برگشت ارسال به تولید پروژه، مصرف پروژه، برگشت مصرف پروژه، برگشت مصرف پروژه، تحویل دارایی ثابت به پروژه، برگشت تحویل دارایی ثابت به پروژه، ارسال ضایعات پروژه، برگشت ارسال ضایعات پروژه، دریافت ضایعات پروژه، **پروژه** می باشد.\n* طرف مقابل در اسناد تحویل فروش، برگشت تحویل فروش، **مشتری** می باشد.\n* طرف مقابل در اسناد دریافت امانی دیگران نزد ما، برگشت دریافت امانی دیگران نزد ما، ارسال امانی ما به دیگران، برگشت ارسال امانی ما به دیگران، شخص/شرکت **طرف حساب امانی** می باشد.\n* طرف مقابل در اسناد رسید دائم سایر، حواله دائم سایر، رسید ضایعات سایر، حواله ضایعات سایر، **شخص/شرکت با کلیه ی نقش های مشتری، تأمین کننده، کارمند، پیمانکار، تنخواه دار، صندوقدار، حمل کننده، کارمند فروش، طرف حساب امانی و سایر نقش ها** می باشد.\n* در اسناد رسید و حواله انتقال بین انبار، به جای فیلد طرف مقابل، **انبار مقابل** را خواهیم داشت که لیستی از **انبارها** را نمایش می دهد\n\n# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: مرکز هزینه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا\nویژگی های الگوی سند انبار برگشت تحویل دارایی ثابت به مرکز عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: مرکز هزینه (غیرقابل تغییر)\n* الگوی سند عطف: تحویل دارایی ثابت به مرکز (غیرقابل تغییر)\nویژگی های الگوی سند انبار تحویل دارایی ثابت به پروژه عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا\nویژگی های الگوی سند انبار برگشت تحویل دارایی ثابت به پروژه عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی و ساختنی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا\n\n# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n.\n* اطلاعات تکمیلی دریافت ضایعات مرکز شامل شماره دستور تولید، شماره سفارش تولید، شماره عملیات تولید، شیفت تولید و تاریخ تولید می باشد.\n* اطلاعات تکمیلی دریافت ضایعات پروژه شامل شماره دستور تولید، شماره سفارش تولید، شماره عملیات تولید، شیفت تولید و تاریخ تولید می باشد.\n* اطلاعات تکمیلی حواله انتقال بین انبار شامل شماره بازرسی کیفیت، شماره چک لیست، شماره آزمایشگاه، تایید ارفاقی، نتیجه بازرسی، نام راننده، نام خودرو، شماره پلاک، شماره بارنامه، تاریخ بارنامه و تلفن راننده می باشد.\n* اطلاعات تکمیلی حواله انتقال بین انبار شامل شماره بازرسی کیفیت، شماره چک لیست، شماره آزمایشگاه، تایید ارفاقی، نتیجه بازرسی، نام راننده، نام خودرو، شماره پلاک، شماره بارنامه، تاریخ بارنامه و تلفن راننده می باشد.\n* اطلاعات تکمیلی تحویل فروش شامل شماره سفارش فروش، شماره فاکتور فروش، مرکز فروش، فروشگاه، تحویل دهنده، شماره برگه باسکول، نام راننده، نام خودرو، شماره پلاک، شماره بارنامه، تاریخ بارنامه و تلفن راننده می باشد\n\n# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: طرف حساب امانی (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت دریافت امانی دیگران نزد ما عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: طرف حساب امانی (غیرقابل تغییر)\n* الگوی سند عطف: دریافت امانی دیگران نزد ما (غیرقابل تغییر)\nویژگی های الگوی سند انبار ارسال امانی ما به دیگران عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: طرف حساب امانی (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت ارسال امانی ما به دیگران عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n\n# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* سند مبنا: درخواست کالا (غیرقابل تغییر)\nویژگی های الگوی سند انبار رسید انتقال بین انبار عبارت است از:\n* نوع سند: انتقال بین انبار (غیرقابل تغییر)\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* الگوی سند عطف: حواله انتقال بین انبار (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت ارسال ضایعات مرکز عبارت است از:\n* نوع سند: ضایعات (غیرقابل تغییر)\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: مشتری (غیرقابل تغییر)\nویژگی های الگوی سند انبار برگشت تحویل فروش عبارت است از:\n* نوع سند: فروش (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: مشتری (غیرقابل تغییر)\n* مبناها: سفارش فروش، فاکتور فروش\nویژگی های الگوی سند انبار دریافت امانی دیگران نزد ما عبارت است از:\n* نوع سند: امانی (غیرقابل تغییر)\n\n# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: مرکز هزینه (غیرقابل تغییر)\n* الگوی سند عطف: مصرف مرکز (غیرقابل تغییر)\nویژگی های الگوی سند انبار مصرف پروژه عبارت است از:\n* نوع سند: مصرف (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* سند مبنا: درخواست کالا\nویژگی های الگوی سند انبار برگشت مصرف پروژه عبارت است از:\n* نوع سند: مصرف (غیرقابل تغییر)\n* جهت سند: ورودی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n* نوع کارکرد: خریدنی، ساختنی، قابل فروش و غیر موجودی\n* نوع طرف مقابل: پروژه (غیرقابل تغییر)\n* الگوی سند عطف: مصرف پروژه (غیرقابل تغییر)\nویژگی های الگوی سند انبار تحویل دارایی ثابت به مرکز عبارت است از:\n* نوع سند: تحویل دارایی ثابت (غیرقابل تغییر)\n* جهت سند: خروجی (غیرقابل تغییر)\n* نوع تأثیر بر موجودی: دائم (غیرقابل تغییر)\n\n# سند انبار سند انبار\n### فهرست سند انبار\nدر صفحه ی فهرست سند انبار می توان لیستی از اسناد انبار تعریف شده در سیستم را مشاهده کرد. ستون های قابل نمایش در فهرست سند انبار عبارتند از شماره سند، الگوی سند، نوع سند، انبار، تاریخ، وضعیت سند، وضعیت قیمت گذاری، وضعیت سند حسابداری و توضیحات.\nبرای مشاهده­ی لیست سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست سند انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2\n\n# الگوی سند انبار\nدر سیستم انبار، **برای ثبت گردش کالا از ثبت سند استفاده می شود. با توجه به رویدادی که در واقعیت اتفاق می افتند انباردار از الگوی سند مناسب آن استفاده می کند. از آنجایی که برای ثبت سند انبار هر شرکت می تواند علاوه بر اطلاعات اجباری هر سند، اطلاعات دیگری را به منظور استفاده در گزارش ها و فرایندهای انبار استفاده نماید، در الگوی سند انبار می توان آنها را تعریف و تنظیم نمود.** **در این بخش اسناد انبار به همراه همه فیلدهای استاندارد موجود در سیستم آمده است.**\nبرای ثبت سند انبار ابتدا لازم است شرکت و الگوی مناسب برای ثبت سند انتخاب شود. در صورتی که الگو و شرکت انتخابی برای کاربر، جز موارد پرکاربرد برای کاربر است، کاربر می تواند افزودن به منو را انتخاب کرده و در این حالت یک منو با عنوان الگوهای سند منتخب به منو اضافه شده و در زیر آن الگوی انتخابی اضافه می گردد.\nاز فرم الگوهای اسناد انبار به منظور تنظیم الگوهای مورد هر نیاز استفاده می شود. الگوهای استاندارد در انبار بر اساس کارکردهای یک انبار عمومی شناسایی شده و در سیستم قرار گرفته است. در ابتدای شروع به کار سیستم نیاز است، از استقرار الگوی سند انبار به منظور ایجاد الگوهای استاندارد استفاده می شود. الگوهای سند انبار دارای بخش های اطلاعات اصلی، سایر طرف مقابل ها، اطلاعات تکمیلی و فیلدهای اضافه می باشد.\n\n### فهرست الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\n\n# انبار\n### مراحل تعریف انبار\nبرای تعریف انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، اطلاعات پایه، انبار، گزینه معرفی انبار (+) را انتخاب نمایید.\nبرای معرفی انبار در منوی لجستیک ابتدا کد و عنوان انبار را تعریف کرده سپس مرکز نگهداری و نوع انبار را به آن اختصاص می دهیم. در پایان نیز در قسمت الگوهای مرتبط، الگوهای سند مجاز برای استفاده در این انبار را انتخاب می کنیم.\nگزینه های بالای صفحه ی ایجاد انبار جدید به شرح زیر می باشد:\n1. نام شرکت: شرکتی را که در آن انبار ایجاد می کنیم نمایش می دهد.\n2. ذخیره: این گزینه امکان \"ذخیره\" و “ذخیره و جدید” انبار جدید را فراهم می کند.\n3. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم معرفی انبار را فراهم می کند.\n4. سایر عملیات: این گزینه امکان ایجاد انبار جدید و نمایش فهرست انبار را فراهم می سازد.\n\n\n# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\nبرای تعریف الگوی سند انبار از الگوی ثبت سند انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای تعریف الگوی سند انبار ابتدا لازم است از فهرست الگوهای استاندارد یکی از الگوها انتخاب شده و وارد فرم مشاهده و ویرایش آن شود.\nدر مشاهده الگوهای سند انبار 4 بخش زیر وجود دارد\n1. اطلاعات اصلی\n2. سایر طرف مقابل ها\n3. اطلاعات تکمیلی\n4. فیلدهای اضافه\nدر بخش اطلاعات اصلی فیلدهای زیر تکمیل می گردد:\n1. کد الگو که غیرقابل ویرایش است.\n2. عنوان الگو که عنوان پیشفرض نمایش داده شده و کاربر می تواند عنوان مورد نظر خود را وارد نماید.\n3. فیلدهای نوع سند، جهت سند، نوع خرید (در اسناد خرید) و نوع تاثیر بر موجودی غیرقابل تغییر بوده و در الگوها قرار گرفته است.\n4. تعداد اقلام سند، تعداد مجاز ردیف های سند انبار است که به صورت پیشفرض 200 ردیف بوده و حداکثر میتواند 500 رکورد باشد.\n5. فیلدهای اجباری و ویرایش درقلم می تواند برای طرف مقابل برای استفاده از امکان تغییر طرف مقابل در اقلام سند انبار استفاده شود.\n6"]

    mock_detected_modules_lst = 'انبار'
    # 2. Act
    result = await prepare_final_context(mock_query, mock_db_index)

    # 3. Assert
    assert result == mock_handle_single.return_value
    mock_retrieve_context.assert_called_once_with(mock_query, database_index='../VectorDB', input_modules=None)
    mock_handle_single.assert_called_once_with(mock_context, mock_detected_modules_lst)
    # Ensure uniformity check was skipped
    mock_is_uniform.assert_not_called()
    mock_handle_clear.assert_not_called()
    mock_handle_clarify.assert_not_called()

@pytest.mark.asyncio
@patch("src.logic._handle_clarification_case")
@patch("src.logic._handle_clear_preference_case")
@patch("src.logic._handle_single_module_case")
@patch("src.logic.is_somewhat_uniform", new_callable=AsyncMock)
@patch("src.logic.retrieve_context_with_metadata", new_callable=AsyncMock)
async def test_prepare_final_context_clear_preference_detected(
    mock_retrieve_context, 
    mock_is_uniform, 
    mock_handle_single, 
    mock_handle_clear,
    mock_handle_clarify
):
    """
    Tests Path 4: Multiple modules detected, but 'is_somewhat_uniform'
    returns False (meaning a clear preference).
    """
    # 1. Arrange
    mock_query = 'چطوری سند بزنم'
    mock_context = [{"text": "# معرفی دفتر\nبرای صدور سند حسابداری نیاز است دفتر در سیستم تعریف شود و ساختار حساب و ارز آن دفتر نیز مشخص گردد. برای اینکار از مسیر منوی اصلی/حسابداری مالی/ دفتر کل/ اطلاعات پایه/ دفتر را انتخاب می‌کنیم.\nفهرست دفترها باز می‌شود، با استفاده از گزینه جدید در بالا و سمت چپ صفحه به صفحه معرفی دفتر جدید می‌رویم.\nکد و عنوان دفتر را مشخص می‌کنیم، ساختار حساب را و ارز اصلی را انتخاب کرده و اگر این دفتر، دفتر اصلی سیستم است یعنی دفاتر قانونی شرکت با آن تهیه می‌شود، گزینه اصلی را انتخاب می‌کنیم.\nپس از آن صفحه ذخیره می‌شود.\nتصویر 1\n* در چند شرکتی دفتر در سطح گروه (مشترک) تعریف می‌شود و به شرکت‌ها گسترش داده می‌شود.\n", "index": 37, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# صدور سند حسابداری با ارز عملیاتی\n## اطلاعات اقلام سند حسابداری\n### امکانات بخش اقلام سند حسابداری\n.\n* در صورت انتخاب ذخیره یادداشت، وضعیت سند یادداشت شده و در گزارشات آثار اسناد یادداشت مشاهده نخواهد شد.\nپس از ذخیره سند حسابداری، کلیدهای چاپ، بارگذاری مجدد و حذف در بالای صفحه نمایش داده می‌شوند.\n* چاپ سند: در صورت انتخاب گزینه چاپ، سند حسابداری با الگوی چاپ پیش فرض نمایش داده خواهد شد که می‌توانید به صورت فایل ذخیره کنید و یا پرینت بگیرید.\nهمچنین امکان چاپ سند با سایر الگوهای چاپ سند تعریف شده وجود دارد.\nبا انتخاب کلید سه نقطه بالای سند، میتوانید یک سند حسابداری جدید ایجاد کنید و یا وارد صفحه فهرست اسناد حسابداری شوید.", "index": 14, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# **انتقال**\n## **سند رسید انتقال**\n* + 1. ثبت خودکار سند رسید انتقال\nبا تایید سند اعلامیه انتقال یا وصول انتقال، در صورتی که ثبت خودکار سند وصول انتقال یا رسید انتقال در الگوی اسناد مربوطه فعال شده باشد، سند وصول انتقال یا رسید انتقال به صورت خودکار با وضعیت تعیین شده در الگوی اسناد ثبت می شود، در غیر این صورت باید وصول انتقال یا رسید انتقال به صورت دستی توسط کاربر ثبت شود.\nهمچنین از طریق کلید صدور وصول انتقال یا رسید انتقال در قسمت سه نقطه بالای صفحه اعلامیه انتقال یا وصول انتقال، می توان وصول انتقال یا رسید انتقال را به صورت خودکار و با وضعیت تعیین شده در الگوی سند مربوطه صادر نمود.\n* + 1. ثبت دستی سند رسید انتقال\nجهت ثبت دستی سند رسید انتقال، پس از تکمیل اطلاعات سربرگ سند، در بخش اقلام ابتدا در نوع منبع مقصد موردنظر، منبع مقصد و منبع مبدا مشخص می شود. سپس در سلکتور اعلامیه انتقال یا وصول انتقال، اعلامیه انتقال یا وصول انتقال موردنظر جستجو و انتخاب می شود. در این لیست، اعلامیه یا وصول انتقال های تایید شده از نوع مربوطه که هنوز رسید نشده اند نمایش داده می شود", "index": 31, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# **رسید دریافت**\n## **فهرست رسیدهای دریافت**\n.\nآیکون کپی لینک نما: با کلیک روی این آیکون در فهرست ها، صفحه با فیلتر ها و نمای انتخاب شده کپی میشود و میتوانید این لینک را با افراد دیگر به اشتراک بگذارید.\nدر صورت انتخاب یک یا چند سند در صفحه فهرست، در سمت چپ بالای صفحه 2 گزینه مشاهده میکنید:\nچاپ سند: با انتخاب این گزینه می توانید به صورت گروهی از اسناد انتخابی چاپ بگیرید.\nحذف سند: با انتخاب این گزینه سند یا اسناد انتخابی شما حذف میشوند.\n(توجه داشته باشید اسناد در وضعیت ثبت شده قابلیت حذف دارند)\nدر پایین همه فهرست ها شما میتوانید تعداد موارد قابل نمایش در صفحه را از بین 20،10، 50 و 100 مورد انتخاب کنید.\nمیتوانید صفحه مورد نظر خود را از سلکتور انتخاب کنید و یا با کلید های بعدی، قبلی، صفحه اول و یا صفحه آخر بین صفحات جا به جا شوید.\nهمچنین برای مشاهده کل تعداد موجود در فهرست میتوانید از کلید تعداد کل استفاده کنید.\nدر بالای صفحه فهرست ها بخش جستجو و فیلتر قابل مشاهده است که از طریق آن می توانید بر اساس فیلترهای مختلف نتایج دلخواه را مشاهده کنید.", "index": 32, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# **اعلامیه پرداخت**\n## **فهرست اعلامیه های پرداخت**\n.\nآیکون کپی لینک نما: با کلیک روی این آیکون در فهرست ها، صفحه با فیلتر ها و نمای انتخاب شده کپی میشود و میتوانید این لینک را با افراد دیگر به اشتراک بگذارید.\nدر صورت انتخاب یک یا چند سند در صفحه فهرست، در سمت چپ بالای صفحه 2 گزینه مشاهده میکنید:\nچاپ سند: با انتخاب این گزینه می توانید به صورت گروهی از اسناد انتخابی چاپ بگیرید.\nحذف سند: با انتخاب این گزینه سند یا اسناد انتخابی شما حذف میشوند.\n(توجه داشته باشید اسناد در وضعیت ثبت شده قابلیت حذف دارند)\nدر پایین همه فهرست ها شما میتوانید تعداد موارد قابل نمایش در صفحه را از بین 20،10، 50 و 100 مورد انتخاب کنید.\nمیتوانید صفحه مورد نظر خود را از سلکتور انتخاب کنید و یا با کلید های بعدی، قبلی، صفحه اول و یا صفحه آخر بین صفحات جا به جا شوید.\nهمچنین برای مشاهده کل تعداد موجود در فهرست میتوانید از کلید تعداد کل استفاده کنید.\nدر بالای صفحه فهرست ها بخش جستجو و فیلتر قابل مشاهده است که از طریق آن می توانید بر اساس فیلترهای مختلف نتایج دلخواه را مشاهده کنید.", "index": 33, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# **انتقال**\n## **سند رسید انتقال**\n. در این صفحه تاریخ و شماره فرعی و شرح سند حسابداری وارد می شود و با زدن کلید صدور سند حسابداری، سند حسابداری اعلامیه انتقال یا رسید انتقال با نوع سند دریافت و پرداخت در دفترکل صادر خواهد شد. برای مشاهده یا حذف سند حسابداری نیز می توان از کلیدهای مربوطه استفاده کرد.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nاز طریق امکان نمایش اسناد مرتبط در قسمت سه نقطه بالای صفحه همه اسناد انتقال، می توان اسناد قبلی و بعدی سند مورد نظر را مشاهده نمود. در صفحه اسناد مرتبط با استفاده از کلیک روی لینک شماره سند می توان سند مرتبط موردنظر را باز کرد.", "index": 38, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# **عملیات استقرار اسناد دریافتنی**\n## **فهرست عملیات استقرار اسناد دریافتنی**\n.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nجهت صدور سند بعد از تکمیل اطلاعات سربرگ سند، در بخش اقلام باید قلم موردنظر را از سلکتور انتخاب و سایر فیلدهای مورد نیاز را تکمیل نمود. اقلامی در سلکتور نمایش داده می شوند که قابلیت صدور سند فعلی برای آنها وجود داشته باشد.\nدر فهرست اسناد، با کلیک روی نام سر ستون امکان مرتب سازی وجود دارد، با کلیک دوباره ترتیب عوض میشود و با کلیک بعدی به حالت اولیه باز میگردد.\nامکان جا به جایی ستون ها با گرفتن و کشیدن آنها وجود دارد.\nبا استفاده از علامت چرخ دنده گوشه سمت چپ میتوانید از تنظیمات مد نظر خود برای فهرست ها استفاده کنید، با کلیک بر روی این علامت بخش های زیر را مشاهده خواهید کرد:\nستون ها: امکان انتخاب یا حذف ستون های مد نظر شما از فهرست در اینجا وجود دارد", "index": 20, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# **موجودی ابتدای سال**\n## **اطلاعات اقلام موجودی ابتدای سال**\n.\nدر صورتی که وضعیت یکی از اقلام سند، برگشت از تایید شود، وضعیت سند به در حال تایید تغییر می یابد و با تایید مجدد سند وضعیت به تایید شده تبدیل می شود.\nدر صورت نیاز به حذف اقلام، با انتخاب اقلام مورد نظر، کلید حذف نمایش داده می شود و می توان اقلام انتخابی را حذف کرد.\nهمچنین در صورت نیاز به کپی اقلام انتخابی می توان از طریق کلید ایجاد کپی، اقلام انتخاب شده را کپی نمود.\n**جمع کل:** در سمت چپ صفحه سند، یک بخش با نام جمع کل قرار گرفته است که به صورت مجزا مجموع مبالغ به تفکیک انواع قلم و جمع کل سند را به ارز عملیاتی (و ارز های گزارشگری در صورت فعال بودن) در هر لحظه نمایش می دهد.\nپس از ذخیره سند، کلیدهای تغییر وضعیت، بارگذاری مجدد و حذف در بالای صفحه نمایش داده میشوند.\nبا انتخاب کلید سه نقطه بالای سند، میتوانید با زدن کلید \"جدید\" یک سند جدید ایجاد کنید و یا با زدن کلید \"نمایش فهرست\" وارد صفحه فهرست اسناد شوید.", "index": 17, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# **عملیات اسناد پرداختنی**\n## **فهرست عملیات اسناد پرداختنی**\n.\nجهت صدور سند بعد از تکمیل اطلاعات سربرگ سند، در بخش اقلام باید قلم موردنظر را از سلکتور انتخاب و سایر فیلدهای مورد نیاز را تکمیل نمود. اقلامی در سلکتور نمایش داده می شوند که قابلیت صدور سند فعلی برای آنها وجود داشته باشد.\nامکانات مرتبط با سند حسابداری شامل صدور سند حسابداری، حذف سند حسابداری، و مشاهده سند حسابداری نیز از این همین بخش در دسترس می باشد. در صورتی که استقرار حساب ها به درستی انجام شده باشد، با انتخاب صدور سند حسابداری صفحه صدور سند حسابداری باز می شود. در این صفحه تاریخ و شماره فرعی و شرح سند حسابداری وارد می شود و با زدن کلید صدور سند حسابداری، سند حسابداری با نوع سند دریافت و پرداخت در دفترکل صادر خواهد شد. برای مشاهده یا حذف سند حسابداری نیز می توان از کلیدهای مربوطه استفاده کرد.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nدر فهرست اسناد، با کلیک روی نام سر ستون امکان مرتب سازی وجود دارد، با کلیک دوباره ترتیب عوض میشود و با کلیک بعدی به حالت اولیه باز میگردد", "index": 35, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# **عملیات اسناد دریافتنی**\n## **فهرست عملیات اسناد دریافتنی**\n.\nجهت صدور سند بعد از تکمیل اطلاعات سربرگ سند، در بخش اقلام باید قلم موردنظر را از سلکتور انتخاب و سایر فیلدهای مورد نیاز را تکمیل نمود. اقلامی در سلکتور نمایش داده می شوند که قابلیت صدور سند فعلی برای آنها وجود داشته باشد.\nامکانات مرتبط با سند حسابداری شامل صدور سند حسابداری، حذف سند حسابداری، و مشاهده سند حسابداری نیز از این همین بخش در دسترس می باشد. در صورتی که استقرار حساب ها به درستی انجام شده باشد، با انتخاب صدور سند حسابداری صفحه صدور سند حسابداری باز می شود. در این صفحه تاریخ و شماره فرعی و شرح سند حسابداری وارد می شود و با زدن کلید صدور سند حسابداری، سند حسابداری با نوع سند دریافت و پرداخت در دفترکل صادر خواهد شد. برای مشاهده یا حذف سند حسابداری نیز می توان از کلیدهای مربوطه استفاده کرد.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nدر فهرست اسناد، با کلیک روی نام سر ستون امکان مرتب سازی وجود دارد، با کلیک دوباره ترتیب عوض میشود و با کلیک بعدی به حالت اولیه باز میگردد", "index": 34, "module": "خزانه داری", "source": "treasury.csv"}]
    mock_detected_modules = 'خزانه داری'
    mock_db='../VectorDB'
    
    mock_retrieve_context.return_value = mock_context
    # is_somewhat_uniform returns (False=not uniform, mean=...)
    mock_is_uniform.return_value = (False, 5)
    mock_handle_clear.return_value = [False, ["خزانه داری"], ["# معرفی دفتر\nبرای صدور سند حسابداری نیاز است دفتر در سیستم تعریف شود و ساختار حساب و ارز آن دفتر نیز مشخص گردد. برای اینکار از مسیر منوی اصلی/حسابداری مالی/ دفتر کل/ اطلاعات پایه/ دفتر را انتخاب می‌کنیم.\nفهرست دفترها باز می‌شود، با استفاده از گزینه جدید در بالا و سمت چپ صفحه به صفحه معرفی دفتر جدید می‌رویم.\nکد و عنوان دفتر را مشخص می‌کنیم، ساختار حساب را و ارز اصلی را انتخاب کرده و اگر این دفتر، دفتر اصلی سیستم است یعنی دفاتر قانونی شرکت با آن تهیه می‌شود، گزینه اصلی را انتخاب می‌کنیم.\nپس از آن صفحه ذخیره می‌شود.\nتصویر 1\n* در چند شرکتی دفتر در سطح گروه (مشترک) تعریف می‌شود و به شرکت‌ها گسترش داده می‌شود.\n", "# صدور سند حسابداری با ارز عملیاتی\n## اطلاعات اقلام سند حسابداری\n### امکانات بخش اقلام سند حسابداری\n.\n* در صورت انتخاب ذخیره یادداشت، وضعیت سند یادداشت شده و در گزارشات آثار اسناد یادداشت مشاهده نخواهد شد.\nپس از ذخیره سند حسابداری، کلیدهای چاپ، بارگذاری مجدد و حذف در بالای صفحه نمایش داده می‌شوند.\n* چاپ سند: در صورت انتخاب گزینه چاپ، سند حسابداری با الگوی چاپ پیش فرض نمایش داده خواهد شد که می‌توانید به صورت فایل ذخیره کنید و یا پرینت بگیرید.\nهمچنین امکان چاپ سند با سایر الگوهای چاپ سند تعریف شده وجود دارد.\nبا انتخاب کلید سه نقطه بالای سند، میتوانید یک سند حسابداری جدید ایجاد کنید و یا وارد صفحه فهرست اسناد حسابداری شوید.", "# **انتقال**\n## **سند رسید انتقال**\n* + 1. ثبت خودکار سند رسید انتقال\nبا تایید سند اعلامیه انتقال یا وصول انتقال، در صورتی که ثبت خودکار سند وصول انتقال یا رسید انتقال در الگوی اسناد مربوطه فعال شده باشد، سند وصول انتقال یا رسید انتقال به صورت خودکار با وضعیت تعیین شده در الگوی اسناد ثبت می شود، در غیر این صورت باید وصول انتقال یا رسید انتقال به صورت دستی توسط کاربر ثبت شود.\nهمچنین از طریق کلید صدور وصول انتقال یا رسید انتقال در قسمت سه نقطه بالای صفحه اعلامیه انتقال یا وصول انتقال، می توان وصول انتقال یا رسید انتقال را به صورت خودکار و با وضعیت تعیین شده در الگوی سند مربوطه صادر نمود.\n* + 1. ثبت دستی سند رسید انتقال\nجهت ثبت دستی سند رسید انتقال، پس از تکمیل اطلاعات سربرگ سند، در بخش اقلام ابتدا در نوع منبع مقصد موردنظر، منبع مقصد و منبع مبدا مشخص می شود. سپس در سلکتور اعلامیه انتقال یا وصول انتقال، اعلامیه انتقال یا وصول انتقال موردنظر جستجو و انتخاب می شود. در این لیست، اعلامیه یا وصول انتقال های تایید شده از نوع مربوطه که هنوز رسید نشده اند نمایش داده می شود", "# **رسید دریافت**\n## **فهرست رسیدهای دریافت**\n.\nآیکون کپی لینک نما: با کلیک روی این آیکون در فهرست ها، صفحه با فیلتر ها و نمای انتخاب شده کپی میشود و میتوانید این لینک را با افراد دیگر به اشتراک بگذارید.\nدر صورت انتخاب یک یا چند سند در صفحه فهرست، در سمت چپ بالای صفحه 2 گزینه مشاهده میکنید:\nچاپ سند: با انتخاب این گزینه می توانید به صورت گروهی از اسناد انتخابی چاپ بگیرید.\nحذف سند: با انتخاب این گزینه سند یا اسناد انتخابی شما حذف میشوند.\n(توجه داشته باشید اسناد در وضعیت ثبت شده قابلیت حذف دارند)\nدر پایین همه فهرست ها شما میتوانید تعداد موارد قابل نمایش در صفحه را از بین 20،10، 50 و 100 مورد انتخاب کنید.\nمیتوانید صفحه مورد نظر خود را از سلکتور انتخاب کنید و یا با کلید های بعدی، قبلی، صفحه اول و یا صفحه آخر بین صفحات جا به جا شوید.\nهمچنین برای مشاهده کل تعداد موجود در فهرست میتوانید از کلید تعداد کل استفاده کنید.\nدر بالای صفحه فهرست ها بخش جستجو و فیلتر قابل مشاهده است که از طریق آن می توانید بر اساس فیلترهای مختلف نتایج دلخواه را مشاهده کنید.", "# **اعلامیه پرداخت**\n## **فهرست اعلامیه های پرداخت**\n.\nآیکون کپی لینک نما: با کلیک روی این آیکون در فهرست ها، صفحه با فیلتر ها و نمای انتخاب شده کپی میشود و میتوانید این لینک را با افراد دیگر به اشتراک بگذارید.\nدر صورت انتخاب یک یا چند سند در صفحه فهرست، در سمت چپ بالای صفحه 2 گزینه مشاهده میکنید:\nچاپ سند: با انتخاب این گزینه می توانید به صورت گروهی از اسناد انتخابی چاپ بگیرید.\nحذف سند: با انتخاب این گزینه سند یا اسناد انتخابی شما حذف میشوند.\n(توجه داشته باشید اسناد در وضعیت ثبت شده قابلیت حذف دارند)\nدر پایین همه فهرست ها شما میتوانید تعداد موارد قابل نمایش در صفحه را از بین 20،10، 50 و 100 مورد انتخاب کنید.\nمیتوانید صفحه مورد نظر خود را از سلکتور انتخاب کنید و یا با کلید های بعدی، قبلی، صفحه اول و یا صفحه آخر بین صفحات جا به جا شوید.\nهمچنین برای مشاهده کل تعداد موجود در فهرست میتوانید از کلید تعداد کل استفاده کنید.\nدر بالای صفحه فهرست ها بخش جستجو و فیلتر قابل مشاهده است که از طریق آن می توانید بر اساس فیلترهای مختلف نتایج دلخواه را مشاهده کنید.", "# **انتقال**\n## **سند رسید انتقال**\n. در این صفحه تاریخ و شماره فرعی و شرح سند حسابداری وارد می شود و با زدن کلید صدور سند حسابداری، سند حسابداری اعلامیه انتقال یا رسید انتقال با نوع سند دریافت و پرداخت در دفترکل صادر خواهد شد. برای مشاهده یا حذف سند حسابداری نیز می توان از کلیدهای مربوطه استفاده کرد.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nاز طریق امکان نمایش اسناد مرتبط در قسمت سه نقطه بالای صفحه همه اسناد انتقال، می توان اسناد قبلی و بعدی سند مورد نظر را مشاهده نمود. در صفحه اسناد مرتبط با استفاده از کلیک روی لینک شماره سند می توان سند مرتبط موردنظر را باز کرد.", "# **عملیات استقرار اسناد دریافتنی**\n## **فهرست عملیات استقرار اسناد دریافتنی**\n.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nجهت صدور سند بعد از تکمیل اطلاعات سربرگ سند، در بخش اقلام باید قلم موردنظر را از سلکتور انتخاب و سایر فیلدهای مورد نیاز را تکمیل نمود. اقلامی در سلکتور نمایش داده می شوند که قابلیت صدور سند فعلی برای آنها وجود داشته باشد.\nدر فهرست اسناد، با کلیک روی نام سر ستون امکان مرتب سازی وجود دارد، با کلیک دوباره ترتیب عوض میشود و با کلیک بعدی به حالت اولیه باز میگردد.\nامکان جا به جایی ستون ها با گرفتن و کشیدن آنها وجود دارد.\nبا استفاده از علامت چرخ دنده گوشه سمت چپ میتوانید از تنظیمات مد نظر خود برای فهرست ها استفاده کنید، با کلیک بر روی این علامت بخش های زیر را مشاهده خواهید کرد:\nستون ها: امکان انتخاب یا حذف ستون های مد نظر شما از فهرست در اینجا وجود دارد", "# **موجودی ابتدای سال**\n## **اطلاعات اقلام موجودی ابتدای سال**\n.\nدر صورتی که وضعیت یکی از اقلام سند، برگشت از تایید شود، وضعیت سند به در حال تایید تغییر می یابد و با تایید مجدد سند وضعیت به تایید شده تبدیل می شود.\nدر صورت نیاز به حذف اقلام، با انتخاب اقلام مورد نظر، کلید حذف نمایش داده می شود و می توان اقلام انتخابی را حذف کرد.\nهمچنین در صورت نیاز به کپی اقلام انتخابی می توان از طریق کلید ایجاد کپی، اقلام انتخاب شده را کپی نمود.\n**جمع کل:** در سمت چپ صفحه سند، یک بخش با نام جمع کل قرار گرفته است که به صورت مجزا مجموع مبالغ به تفکیک انواع قلم و جمع کل سند را به ارز عملیاتی (و ارز های گزارشگری در صورت فعال بودن) در هر لحظه نمایش می دهد.\nپس از ذخیره سند، کلیدهای تغییر وضعیت، بارگذاری مجدد و حذف در بالای صفحه نمایش داده میشوند.\nبا انتخاب کلید سه نقطه بالای سند، میتوانید با زدن کلید \"جدید\" یک سند جدید ایجاد کنید و یا با زدن کلید \"نمایش فهرست\" وارد صفحه فهرست اسناد شوید.", "# **عملیات اسناد پرداختنی**\n## **فهرست عملیات اسناد پرداختنی**\n.\nجهت صدور سند بعد از تکمیل اطلاعات سربرگ سند، در بخش اقلام باید قلم موردنظر را از سلکتور انتخاب و سایر فیلدهای مورد نیاز را تکمیل نمود. اقلامی در سلکتور نمایش داده می شوند که قابلیت صدور سند فعلی برای آنها وجود داشته باشد.\nامکانات مرتبط با سند حسابداری شامل صدور سند حسابداری، حذف سند حسابداری، و مشاهده سند حسابداری نیز از این همین بخش در دسترس می باشد. در صورتی که استقرار حساب ها به درستی انجام شده باشد، با انتخاب صدور سند حسابداری صفحه صدور سند حسابداری باز می شود. در این صفحه تاریخ و شماره فرعی و شرح سند حسابداری وارد می شود و با زدن کلید صدور سند حسابداری، سند حسابداری با نوع سند دریافت و پرداخت در دفترکل صادر خواهد شد. برای مشاهده یا حذف سند حسابداری نیز می توان از کلیدهای مربوطه استفاده کرد.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nدر فهرست اسناد، با کلیک روی نام سر ستون امکان مرتب سازی وجود دارد، با کلیک دوباره ترتیب عوض میشود و با کلیک بعدی به حالت اولیه باز میگردد", "# **عملیات اسناد دریافتنی**\n## **فهرست عملیات اسناد دریافتنی**\n.\nجهت صدور سند بعد از تکمیل اطلاعات سربرگ سند، در بخش اقلام باید قلم موردنظر را از سلکتور انتخاب و سایر فیلدهای مورد نیاز را تکمیل نمود. اقلامی در سلکتور نمایش داده می شوند که قابلیت صدور سند فعلی برای آنها وجود داشته باشد.\nامکانات مرتبط با سند حسابداری شامل صدور سند حسابداری، حذف سند حسابداری، و مشاهده سند حسابداری نیز از این همین بخش در دسترس می باشد. در صورتی که استقرار حساب ها به درستی انجام شده باشد، با انتخاب صدور سند حسابداری صفحه صدور سند حسابداری باز می شود. در این صفحه تاریخ و شماره فرعی و شرح سند حسابداری وارد می شود و با زدن کلید صدور سند حسابداری، سند حسابداری با نوع سند دریافت و پرداخت در دفترکل صادر خواهد شد. برای مشاهده یا حذف سند حسابداری نیز می توان از کلیدهای مربوطه استفاده کرد.\nهمچنین با استفاده از کلید جمع ارزی سند می توانید جمع مبلغ به ارز سند و ارز مبنا را به تفکیک انواع قلم مشاهده نمایید.\nدر فهرست اسناد، با کلیک روی نام سر ستون امکان مرتب سازی وجود دارد، با کلیک دوباره ترتیب عوض میشود و با کلیک بعدی به حالت اولیه باز میگردد"]]
    
    expected_frequencies = Counter({"دفتر کل": 2, "خزانه داری": 8})
    # expected_frequencies = {'خزانه داری': 8, 'دفتر کل': 2}

    # 2. Act
    result = await prepare_final_context(mock_query, mock_db)

    # 3. Assert
    assert result == mock_handle_clear.return_value 
    mock_is_uniform.assert_called_once_with(expected_frequencies)
    # 'sales' is the most frequent (2)
    mock_handle_clear.assert_called_once_with(mock_context, mock_detected_modules)
    mock_handle_single.assert_not_called()
    mock_handle_clarify.assert_not_called()

@pytest.mark.asyncio
# We also need to patch the config dictionary for this test
@patch("src.logic._handle_clarification_case")
@patch("src.logic._handle_clear_preference_case")
@patch("src.logic._handle_single_module_case")
@patch("src.logic.is_somewhat_uniform", new_callable=AsyncMock)
@patch("src.logic.retrieve_context_with_metadata", new_callable=AsyncMock)
async def test_prepare_final_context_needs_clarification(
    mock_retrieve_context, 
    mock_is_uniform, 
    mock_handle_single, 
    mock_handle_clear, 
    mock_handle_clarify
):
    """
    Tests Path 5: Multiple modules detected, and 'is_somewhat_uniform'
    returns True (meaning it's ambiguous).
    """
    # 1. Arrange
    mock_query = 'انواع ماژول های موجود را نام ببر'
    mock_context = [{"text": "# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه اطلاعات معین\n. در این فیلد میتوانید ماژول های مجاز به استفاده از معین مربوطه را مشخص کنید، بعد از انتخاب هر ماژول ، امکان انتخاب در فرم های استقرار حساب ماژول ها و صدور سند حسابداری با معین جاری در ماژول مورد نظر به کاربر داده می شود .\n* اگر بعد از استفاده ( در دفتر کل یا سایر ماژول ها ) امکان صدور سند از ماژول ها برداشته شود، در زمان صدور سند حسابداری از سمت همان ماژول کنترل می شود که معین های دارای این ویژگی استفاده شده باشند .\n* امکان مشاهده اطلاعات همه معین ها در گزارشات دفتر کل ( فارغ از اینکه امکان استفاده در دفتر کل برای آنها انتخاب شده باشد یا نه ) وجود دارد\n* **فعال:** وضعیت حساب معین را نمایش می دهد که می تواند فعال یا غیرفعال باشد.\nحساب معینی که گزینه \"فعال\" آن انتخاب نشده باشد، امکان شرکت در هیچ عملیاتی از جمله صدور سند حسابداری، نگاشت حساب ها، حساب های طرف مقابل، نخواهد داشت.\n* حساب های معین همواره امکان غیر فعال شدن دارند، در صورت فعال نبودن، در زمان صدور سند حسابداری های سیستمی اجازه صدور سند داده نمی‌شود", "index": 29, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# بازاریابی\nبازاریابی به مجموعه فعالیت‌ها و فرایندهایی اطلاق می‌شود که با هدف شناسایی، جذب و علاقه‌مند کردن مشتریان بالقوه پیش از انجام فروش قطعی انجام می‌شوند. این بخش به سازمان‌ها کمک می‌کند تا مسیر حرکت مخاطبان از آشنایی اولیه را به‌صورت دقیق و ساختاریافته مدیریت کنند.\nاطلاعات بازاریابی ماژول مدیریت ارتباط با مشتریان شامل موارد زیر است\n\n## **1-3 کمپین ها**\n### **1-1-3 ایجاد کمپین**\n### **2-1-3 فیلد های کمپین**\n### **3-1-3 مشاهده کمپین**\n### **4-1-3 فهرست کمپین**", "index": 11, "module": "مدیریت ارتباط با مشتری", "source": "crm.csv"}, {"text": "# نوع انبار\n### مراحل تعریف نوع انبار\nبرای تعریف نوع انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، اطلاعات پایه، نوع انبار، گزینه معرفی نوع انبار (+) را انتخاب نمایید.\nمعرفی نوع انبار در منوی لجستیک شامل تعریف کد و عنوان می باشد.\nگزینه های بالای صفحه ی ایجاد نوع انبار جدید به شرح زیر می باشد:\n1. نام شرکت: شرکتی را که در آن نوع انبار ایجاد می کنیم نمایش می دهد.\n2. ذخیره: این گزینه امکان \"ذخیره\" و “ذخیره و جدید” نوع انبار جدید را فراهم می کند.\n3. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم معرفی نوع انبار را فراهم می کند.\n4. سایر عملیات: این گزینه امکان ایجاد نوع انبار جدید و نمایش فهرست نوع انبار را فراهم می سازد.\n", "index": 33, "module": "انبار", "source": "inventory.csv"}, {"text": "# اطلاعات پایه\nاطلاعات پایه در ماژول فروش به داده‌ها و اطلاعاتی اطلاق می‌شود که به عنوان پایه و اساس برای انجام فعالیت‌های فروش و مدیریت فرایندهای مرتبط با آن استفاده می‌شوند. این اطلاعات پایه به سازمان‌ها کمک می‌کند تا فعالیت‌های فروش خود را به صورت کارآمدتر و دقیق‌تر مدیریت کنند.\nاطلاعات پایه ماژول فروش شامل موارد زیر است.\n[ساختار فروش](#_1-1_ساختار_فروش)\n[مدیریت طرف تجاری](#_2-1_مدیریت_طرف)\n[مدیریت اقلام قابل فروش](#_3-1_مدیریت_اقلام)\n[عوامل موثر بر قیمت](#_4-1_عوامل_موثر)\n\n## **1-1 ساختار فروش**\n### **1-1-1 سازمان فروش**\n### **2-2-1 کانال فروش**\n### **3-1-1 بخش فروش**\n### **1-1-4 حوزه های فروش**\n### **5-1-1 دفترهای فروش**\n## **2-1 مدیریت طرف تجاری**\n### **1-2-1 مشتری ها**\n### **2-2-1 گروهبندی مشتری**\n## **3-1 مدیریت اقلام قابل فروش**\n### **1-3-1 کالاها**\n### **2-3-1 خدمت**\n### **3-3-1 گروهبندی کالا/خدمت**\n## **4-1 عوامل موثر بر قیمت**\n### **1-4-1 الگوهای لیست قیمت**\n### **2-4-1 لیست قیمت**\n## **5-1 تخفیف ها**\n## **6-1 عوامل افزاینده**\n## **7-1 اولویت های محاسبه**\n## **8-1 روش های گرد کردن**", "index": 26, "module": "فروش", "source": "sales.csv"}, {"text": "# فرآیند پیش از فروش\n### **2-3-4 فیلد های مشتری**\n. زمان ایجاد حساب (سیستمی / اجباری)\nتاریخ و زمان ایجاد مشتری، برای گزارش‌های زمانی و بررسی تأخیرهای احتمالی.\n18. تاریخ آخرین به‌روزرسانی (سیستمی / اجباری)\nمشخص می‌کند آخرین بار چه زمانی اطلاعات مشتری ویرایش شده‌اند.\nدر بررسی تغییرات و به‌روزرسانی‌ها مفید است.\n19. آدرس‌های مشتری\nامکان ثبت چند آدرس برای مشتری با تعیین نقش هر یک (تحویل کالا، ارسال صورتحساب و...).\nبرای حمل‌ونقل، لجستیک، فاکتوردهی و مطابقت قانونی ضروری است.\n20. گروه‌های عضو\nامکان تخصیص مشتری به گروه‌های از پیش تعریف‌شده مانند \"مشتریان VIP\"، \"استراتژیک\"، یا \"پرتخفیف\".\nبرای اعمال سیاست‌های خاص، فیلترینگ و تحلیل بهتر استفاده می‌شود.\n21. گروه مالیاتی\nمشخص می‌کند مشتری در کدام دسته‌بندی مالیاتی قرار می‌گیرد.\nاز اطلاعات ماژول دفتر کل استفاده می‌کند و در صدور فاکتورها و محاسبات مالی اهمیت دارد.\nاین گروه ها از ماژول فروش فراخوانی میشوند", "index": 15, "module": "مدیریت ارتباط با مشتری", "source": "crm.csv"}, {"text": "# گزارش‎‌‌ها\n## گزارش مقایسه ای\n. انواع سند شامل موارد زیر است:\n+ افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند.\n* سال مالی: از طریق فیلتر سال مالی می توانید محدوده سال های مالی مورد نظر برای اجرای گزارش را تعیین نمایید.\n* نوع مبلغ : در این فیلتر میتوانید مشخص کنید که چه نوع مبلغی را میخواهید مقایسه کنید که شامل موارد زیر است:\n+ مانده : با انتخاب مانده ، مانده های حساب در بازه انتخابی در گزارش نمایش داده میشود.\n+ گردش بدهکار: با انتخاب این مورد گردش بدهکار در بازه انتخابی نمایش داده میشود.\n+ گردش بستانکار: با انتخاب این مورد گردش بستانکار در بازه انتخابی نمایش داده میشود.\n* فیلترهای بیشتر : در فیلتر های بیشتر میتوانید موارد زیر را فیلتر کنید:\n+ ویژگی ارزی : با انتخاب این فیلتر معین های دارای ویژگی ارزی در گزارش نمایش داده میشود", "index": 14, "module": "دفتر کل", "source": "voucher.csv"}, {"text": "# انواع تفصیلی‌\nانواع تفصيل در سيستم به 3 دسته کلی تقسيم مي‌شوند:\n1. نوع تفصيل هايي كه جزو موجوديت هاي عمومي در سيستم هستند و برای همه ماژول‌ها استفاده می‌شوند و شامل موجوديت‌هاي ذیل می‌باشند.\n* شخص حقيقي / شخص حقوقي\n* مركز هزينه\n* پروژه\n* شعبه\n1. نوع تفصيل هايي كه ماژول مرتبط با آنها در سبد محصول وجود دارد. اين دسته از انواع تفصيل شامل دو بخش هستند:\n* ماژول مرتبط با آنها در قفل مشتري وجود دارد: در ماژول مرتبط، فرم معرفي نمونه موجوديت وجود دارد و بعد از ذخيره اوليه فرم، امكان تعريف اطلاعات تفصيل داده مي‌شود. مثل تسهیلات مالی\n* ماژول مرتبط در قفل مشتري وجود ندارد : در ماژول دفتر كل يك فرم با حداقل اطلاعات مورد نیاز بابت هر كدام از اين انواع تفصيل وجود دارد. برای مثال حساب بانکی، صندوق، تنخواه و ....\nدر اين فرم حداقل اطلاعاتي كه نمونه هاي اين موجوديت را معنی‌دار مي كند توسط كاربر ثبت شده و اطلاعات تفصيل مربوط به اين نمونه موجوديت هم مطابق با قواعد اطلاعات تفصيل در دفتر كل ثبت مي شود.\nاین نوع تفصیل‌ها در حال حاضر در سیستم شامل موارد ذیل است:\n* حساب بانکی\n* صندوق\n* تنخواه\n* کالا\n* حوزه قیمت‌گذاری\n* گروه مشتریان\n* گروه کالا و خدمت\n1. نوع تفصيل هاي مورد نياز مشتري كه اطلاعات هويت آنها در سبد محصول وجود ندارد. براي اين انواع تفصيل که تفصیل سایر نام دارند، 10 عدد در سیستم به صورت پیش فرض وجود دارد که کاربر می‌تواند با فعال کردن و تغییر عنوان به عنوان دلخواه مورد استفاده قرار دهد.\nاین انواع تفصیل در سیستم شامل تفصیل سایر 1 تا سایر 10 است.\nامکان معرفی نوع تفصیل به صورت دستی در سیستم وجود ندارد. کاربر اگر بخواهد نوع تفصیل جدید غیر از موارد سیستمی داشته باشد، می‌تواند از انواع تفصیل سایر که حداکثر 10 تا است، استفاده کند.\nاز مسیر منوی اصلی/ حسابداری مالی/ دفتر کل/ حساب‌ها/ نوع تفصیل امکان مشاهده فهرست کل انواع تفصیل موجود در سیستم وجود دارد.\nبا قرار گرفتن روی هر ردیف و کلیک روی عنوان تفصیل می‌توان فهرست حساب‌های تفصیلی هر نوع تفصیل را مشاهده کرد.\nدر صورت وجود حساب تفصیل، امکان حذف نوع تفصیل وجود نخواهد داشت اما همواره برای جلوگیری از استفاده، می‌توانید نوع تفصیل را غیر فعال کنید.\n", "index": 0, "module": "دفتر کل", "source": "voucher.csv"}]
    
    mock_retrieve_context.return_value = mock_context
    mock_database_index = '../VectorDB'
    # is_somewhat_uniform returns (True=uniform, mean=...)
    mock_is_uniform.return_value = (True, 1.75) 
    mock_handle_clarify.return_value = [True, ["انبار", "مدیریت ارتباط با مشتری", "دفتر کل", "فروش"], ["# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه اطلاعات معین\n. در این فیلد میتوانید ماژول های مجاز به استفاده از معین مربوطه را مشخص کنید، بعد از انتخاب هر ماژول ، امکان انتخاب در فرم های استقرار حساب ماژول ها و صدور سند حسابداری با معین جاری در ماژول مورد نظر به کاربر داده می شود .\n* اگر بعد از استفاده ( در دفتر کل یا سایر ماژول ها ) امکان صدور سند از ماژول ها برداشته شود، در زمان صدور سند حسابداری از سمت همان ماژول کنترل می شود که معین های دارای این ویژگی استفاده شده باشند .\n* امکان مشاهده اطلاعات همه معین ها در گزارشات دفتر کل ( فارغ از اینکه امکان استفاده در دفتر کل برای آنها انتخاب شده باشد یا نه ) وجود دارد\n* **فعال:** وضعیت حساب معین را نمایش می دهد که می تواند فعال یا غیرفعال باشد.\nحساب معینی که گزینه \"فعال\" آن انتخاب نشده باشد، امکان شرکت در هیچ عملیاتی از جمله صدور سند حسابداری، نگاشت حساب ها، حساب های طرف مقابل، نخواهد داشت.\n* حساب های معین همواره امکان غیر فعال شدن دارند، در صورت فعال نبودن، در زمان صدور سند حسابداری های سیستمی اجازه صدور سند داده نمی‌شود", "# بازاریابی\nبازاریابی به مجموعه فعالیت‌ها و فرایندهایی اطلاق می‌شود که با هدف شناسایی، جذب و علاقه‌مند کردن مشتریان بالقوه پیش از انجام فروش قطعی انجام می‌شوند. این بخش به سازمان‌ها کمک می‌کند تا مسیر حرکت مخاطبان از آشنایی اولیه را به‌صورت دقیق و ساختاریافته مدیریت کنند.\nاطلاعات بازاریابی ماژول مدیریت ارتباط با مشتریان شامل موارد زیر است\n\n## **1-3 کمپین ها**\n### **1-1-3 ایجاد کمپین**\n### **2-1-3 فیلد های کمپین**\n### **3-1-3 مشاهده کمپین**\n### **4-1-3 فهرست کمپین**", "# نوع انبار\n### مراحل تعریف نوع انبار\nبرای تعریف نوع انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، اطلاعات پایه، نوع انبار، گزینه معرفی نوع انبار (+) را انتخاب نمایید.\nمعرفی نوع انبار در منوی لجستیک شامل تعریف کد و عنوان می باشد.\nگزینه های بالای صفحه ی ایجاد نوع انبار جدید به شرح زیر می باشد:\n1. نام شرکت: شرکتی را که در آن نوع انبار ایجاد می کنیم نمایش می دهد.\n2. ذخیره: این گزینه امکان \"ذخیره\" و “ذخیره و جدید” نوع انبار جدید را فراهم می کند.\n3. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم معرفی نوع انبار را فراهم می کند.\n4. سایر عملیات: این گزینه امکان ایجاد نوع انبار جدید و نمایش فهرست نوع انبار را فراهم می سازد.\n", "# اطلاعات پایه\nاطلاعات پایه در ماژول فروش به داده‌ها و اطلاعاتی اطلاق می‌شود که به عنوان پایه و اساس برای انجام فعالیت‌های فروش و مدیریت فرایندهای مرتبط با آن استفاده می‌شوند. این اطلاعات پایه به سازمان‌ها کمک می‌کند تا فعالیت‌های فروش خود را به صورت کارآمدتر و دقیق‌تر مدیریت کنند.\nاطلاعات پایه ماژول فروش شامل موارد زیر است.\n[ساختار فروش](#_1-1_ساختار_فروش)\n[مدیریت طرف تجاری](#_2-1_مدیریت_طرف)\n[مدیریت اقلام قابل فروش](#_3-1_مدیریت_اقلام)\n[عوامل موثر بر قیمت](#_4-1_عوامل_موثر)\n\n## **1-1 ساختار فروش**\n### **1-1-1 سازمان فروش**\n### **2-2-1 کانال فروش**\n### **3-1-1 بخش فروش**\n### **1-1-4 حوزه های فروش**\n### **5-1-1 دفترهای فروش**\n## **2-1 مدیریت طرف تجاری**\n### **1-2-1 مشتری ها**\n### **2-2-1 گروهبندی مشتری**\n## **3-1 مدیریت اقلام قابل فروش**\n### **1-3-1 کالاها**\n### **2-3-1 خدمت**\n### **3-3-1 گروهبندی کالا/خدمت**\n## **4-1 عوامل موثر بر قیمت**\n### **1-4-1 الگوهای لیست قیمت**\n### **2-4-1 لیست قیمت**\n## **5-1 تخفیف ها**\n## **6-1 عوامل افزاینده**\n## **7-1 اولویت های محاسبه**\n## **8-1 روش های گرد کردن**", "# فرآیند پیش از فروش\n### **2-3-4 فیلد های مشتری**\n. زمان ایجاد حساب (سیستمی / اجباری)\nتاریخ و زمان ایجاد مشتری، برای گزارش‌های زمانی و بررسی تأخیرهای احتمالی.\n18. تاریخ آخرین به‌روزرسانی (سیستمی / اجباری)\nمشخص می‌کند آخرین بار چه زمانی اطلاعات مشتری ویرایش شده‌اند.\nدر بررسی تغییرات و به‌روزرسانی‌ها مفید است.\n19. آدرس‌های مشتری\nامکان ثبت چند آدرس برای مشتری با تعیین نقش هر یک (تحویل کالا، ارسال صورتحساب و...).\nبرای حمل‌ونقل، لجستیک، فاکتوردهی و مطابقت قانونی ضروری است.\n20. گروه‌های عضو\nامکان تخصیص مشتری به گروه‌های از پیش تعریف‌شده مانند \"مشتریان VIP\"، \"استراتژیک\"، یا \"پرتخفیف\".\nبرای اعمال سیاست‌های خاص، فیلترینگ و تحلیل بهتر استفاده می‌شود.\n21. گروه مالیاتی\nمشخص می‌کند مشتری در کدام دسته‌بندی مالیاتی قرار می‌گیرد.\nاز اطلاعات ماژول دفتر کل استفاده می‌کند و در صدور فاکتورها و محاسبات مالی اهمیت دارد.\nاین گروه ها از ماژول فروش فراخوانی میشوند", "# گزارش‎‌‌ها\n## گزارش مقایسه ای\n. انواع سند شامل موارد زیر است:\n+ افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند.\n* سال مالی: از طریق فیلتر سال مالی می توانید محدوده سال های مالی مورد نظر برای اجرای گزارش را تعیین نمایید.\n* نوع مبلغ : در این فیلتر میتوانید مشخص کنید که چه نوع مبلغی را میخواهید مقایسه کنید که شامل موارد زیر است:\n+ مانده : با انتخاب مانده ، مانده های حساب در بازه انتخابی در گزارش نمایش داده میشود.\n+ گردش بدهکار: با انتخاب این مورد گردش بدهکار در بازه انتخابی نمایش داده میشود.\n+ گردش بستانکار: با انتخاب این مورد گردش بستانکار در بازه انتخابی نمایش داده میشود.\n* فیلترهای بیشتر : در فیلتر های بیشتر میتوانید موارد زیر را فیلتر کنید:\n+ ویژگی ارزی : با انتخاب این فیلتر معین های دارای ویژگی ارزی در گزارش نمایش داده میشود", "# انواع تفصیلی‌\nانواع تفصيل در سيستم به 3 دسته کلی تقسيم مي‌شوند:\n1. نوع تفصيل هايي كه جزو موجوديت هاي عمومي در سيستم هستند و برای همه ماژول‌ها استفاده می‌شوند و شامل موجوديت‌هاي ذیل می‌باشند.\n* شخص حقيقي / شخص حقوقي\n* مركز هزينه\n* پروژه\n* شعبه\n1. نوع تفصيل هايي كه ماژول مرتبط با آنها در سبد محصول وجود دارد. اين دسته از انواع تفصيل شامل دو بخش هستند:\n* ماژول مرتبط با آنها در قفل مشتري وجود دارد: در ماژول مرتبط، فرم معرفي نمونه موجوديت وجود دارد و بعد از ذخيره اوليه فرم، امكان تعريف اطلاعات تفصيل داده مي‌شود. مثل تسهیلات مالی\n* ماژول مرتبط در قفل مشتري وجود ندارد : در ماژول دفتر كل يك فرم با حداقل اطلاعات مورد نیاز بابت هر كدام از اين انواع تفصيل وجود دارد. برای مثال حساب بانکی، صندوق، تنخواه و ....\nدر اين فرم حداقل اطلاعاتي كه نمونه هاي اين موجوديت را معنی‌دار مي كند توسط كاربر ثبت شده و اطلاعات تفصيل مربوط به اين نمونه موجوديت هم مطابق با قواعد اطلاعات تفصيل در دفتر كل ثبت مي شود.\nاین نوع تفصیل‌ها در حال حاضر در سیستم شامل موارد ذیل است:\n* حساب بانکی\n* صندوق\n* تنخواه\n* کالا\n* حوزه قیمت‌گذاری\n* گروه مشتریان\n* گروه کالا و خدمت\n1. نوع تفصيل هاي مورد نياز مشتري كه اطلاعات هويت آنها در سبد محصول وجود ندارد. براي اين انواع تفصيل که تفصیل سایر نام دارند، 10 عدد در سیستم به صورت پیش فرض وجود دارد که کاربر می‌تواند با فعال کردن و تغییر عنوان به عنوان دلخواه مورد استفاده قرار دهد.\nاین انواع تفصیل در سیستم شامل تفصیل سایر 1 تا سایر 10 است.\nامکان معرفی نوع تفصیل به صورت دستی در سیستم وجود ندارد. کاربر اگر بخواهد نوع تفصیل جدید غیر از موارد سیستمی داشته باشد، می‌تواند از انواع تفصیل سایر که حداکثر 10 تا است، استفاده کند.\nاز مسیر منوی اصلی/ حسابداری مالی/ دفتر کل/ حساب‌ها/ نوع تفصیل امکان مشاهده فهرست کل انواع تفصیل موجود در سیستم وجود دارد.\nبا قرار گرفتن روی هر ردیف و کلیک روی عنوان تفصیل می‌توان فهرست حساب‌های تفصیلی هر نوع تفصیل را مشاهده کرد.\nدر صورت وجود حساب تفصیل، امکان حذف نوع تفصیل وجود نخواهد داشت اما همواره برای جلوگیری از استفاده، می‌توانید نوع تفصیل را غیر فعال کنید.\n"]]
    
    expected_frequencies = Counter({'دفتر کل': 3, 'مدیریت ارتباط با مشتری': 2, 'انبار': 1, 'فروش': 1})
    expected_proposable = {'مدیریت ارتباط با مشتری', 'خزانه داری', 'فروش', 'دفتر کل', 'مودیان', 'انبار', 'گزارش ساز'}

    # 2. Act
    result = await prepare_final_context(mock_query, mock_database_index)

    # 3. Assert
    assert result == [True, ["انبار", "مدیریت ارتباط با مشتری", "دفتر کل", "فروش"], ["# ساختار حساب ها\n## تعریف اطلاعات ساختار حساب جدید\n### زبانه اطلاعات معین\n. در این فیلد میتوانید ماژول های مجاز به استفاده از معین مربوطه را مشخص کنید، بعد از انتخاب هر ماژول ، امکان انتخاب در فرم های استقرار حساب ماژول ها و صدور سند حسابداری با معین جاری در ماژول مورد نظر به کاربر داده می شود .\n* اگر بعد از استفاده ( در دفتر کل یا سایر ماژول ها ) امکان صدور سند از ماژول ها برداشته شود، در زمان صدور سند حسابداری از سمت همان ماژول کنترل می شود که معین های دارای این ویژگی استفاده شده باشند .\n* امکان مشاهده اطلاعات همه معین ها در گزارشات دفتر کل ( فارغ از اینکه امکان استفاده در دفتر کل برای آنها انتخاب شده باشد یا نه ) وجود دارد\n* **فعال:** وضعیت حساب معین را نمایش می دهد که می تواند فعال یا غیرفعال باشد.\nحساب معینی که گزینه \"فعال\" آن انتخاب نشده باشد، امکان شرکت در هیچ عملیاتی از جمله صدور سند حسابداری، نگاشت حساب ها، حساب های طرف مقابل، نخواهد داشت.\n* حساب های معین همواره امکان غیر فعال شدن دارند، در صورت فعال نبودن، در زمان صدور سند حسابداری های سیستمی اجازه صدور سند داده نمی‌شود", "# بازاریابی\nبازاریابی به مجموعه فعالیت‌ها و فرایندهایی اطلاق می‌شود که با هدف شناسایی، جذب و علاقه‌مند کردن مشتریان بالقوه پیش از انجام فروش قطعی انجام می‌شوند. این بخش به سازمان‌ها کمک می‌کند تا مسیر حرکت مخاطبان از آشنایی اولیه را به‌صورت دقیق و ساختاریافته مدیریت کنند.\nاطلاعات بازاریابی ماژول مدیریت ارتباط با مشتریان شامل موارد زیر است\n\n## **1-3 کمپین ها**\n### **1-1-3 ایجاد کمپین**\n### **2-1-3 فیلد های کمپین**\n### **3-1-3 مشاهده کمپین**\n### **4-1-3 فهرست کمپین**", "# نوع انبار\n### مراحل تعریف نوع انبار\nبرای تعریف نوع انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، اطلاعات پایه، نوع انبار، گزینه معرفی نوع انبار (+) را انتخاب نمایید.\nمعرفی نوع انبار در منوی لجستیک شامل تعریف کد و عنوان می باشد.\nگزینه های بالای صفحه ی ایجاد نوع انبار جدید به شرح زیر می باشد:\n1. نام شرکت: شرکتی را که در آن نوع انبار ایجاد می کنیم نمایش می دهد.\n2. ذخیره: این گزینه امکان \"ذخیره\" و “ذخیره و جدید” نوع انبار جدید را فراهم می کند.\n3. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم معرفی نوع انبار را فراهم می کند.\n4. سایر عملیات: این گزینه امکان ایجاد نوع انبار جدید و نمایش فهرست نوع انبار را فراهم می سازد.\n", "# اطلاعات پایه\nاطلاعات پایه در ماژول فروش به داده‌ها و اطلاعاتی اطلاق می‌شود که به عنوان پایه و اساس برای انجام فعالیت‌های فروش و مدیریت فرایندهای مرتبط با آن استفاده می‌شوند. این اطلاعات پایه به سازمان‌ها کمک می‌کند تا فعالیت‌های فروش خود را به صورت کارآمدتر و دقیق‌تر مدیریت کنند.\nاطلاعات پایه ماژول فروش شامل موارد زیر است.\n[ساختار فروش](#_1-1_ساختار_فروش)\n[مدیریت طرف تجاری](#_2-1_مدیریت_طرف)\n[مدیریت اقلام قابل فروش](#_3-1_مدیریت_اقلام)\n[عوامل موثر بر قیمت](#_4-1_عوامل_موثر)\n\n## **1-1 ساختار فروش**\n### **1-1-1 سازمان فروش**\n### **2-2-1 کانال فروش**\n### **3-1-1 بخش فروش**\n### **1-1-4 حوزه های فروش**\n### **5-1-1 دفترهای فروش**\n## **2-1 مدیریت طرف تجاری**\n### **1-2-1 مشتری ها**\n### **2-2-1 گروهبندی مشتری**\n## **3-1 مدیریت اقلام قابل فروش**\n### **1-3-1 کالاها**\n### **2-3-1 خدمت**\n### **3-3-1 گروهبندی کالا/خدمت**\n## **4-1 عوامل موثر بر قیمت**\n### **1-4-1 الگوهای لیست قیمت**\n### **2-4-1 لیست قیمت**\n## **5-1 تخفیف ها**\n## **6-1 عوامل افزاینده**\n## **7-1 اولویت های محاسبه**\n## **8-1 روش های گرد کردن**", "# فرآیند پیش از فروش\n### **2-3-4 فیلد های مشتری**\n. زمان ایجاد حساب (سیستمی / اجباری)\nتاریخ و زمان ایجاد مشتری، برای گزارش‌های زمانی و بررسی تأخیرهای احتمالی.\n18. تاریخ آخرین به‌روزرسانی (سیستمی / اجباری)\nمشخص می‌کند آخرین بار چه زمانی اطلاعات مشتری ویرایش شده‌اند.\nدر بررسی تغییرات و به‌روزرسانی‌ها مفید است.\n19. آدرس‌های مشتری\nامکان ثبت چند آدرس برای مشتری با تعیین نقش هر یک (تحویل کالا، ارسال صورتحساب و...).\nبرای حمل‌ونقل، لجستیک، فاکتوردهی و مطابقت قانونی ضروری است.\n20. گروه‌های عضو\nامکان تخصیص مشتری به گروه‌های از پیش تعریف‌شده مانند \"مشتریان VIP\"، \"استراتژیک\"، یا \"پرتخفیف\".\nبرای اعمال سیاست‌های خاص، فیلترینگ و تحلیل بهتر استفاده می‌شود.\n21. گروه مالیاتی\nمشخص می‌کند مشتری در کدام دسته‌بندی مالیاتی قرار می‌گیرد.\nاز اطلاعات ماژول دفتر کل استفاده می‌کند و در صدور فاکتورها و محاسبات مالی اهمیت دارد.\nاین گروه ها از ماژول فروش فراخوانی میشوند", "# گزارش‎‌‌ها\n## گزارش مقایسه ای\n. انواع سند شامل موارد زیر است:\n+ افتتاحیه\n+ اختتامیه\n+ بستن حساب ها\n+ تعدیل ماهیت ابتدای سال\n+ تعدیل ماهیت پایان سال\n+ تسعیر ارز اقلام پولی\n+ تسعیر به ارز گزارشگری\n+ عمومی\n+ همه انواع سند سایر ماژول ها\n+ همه انواع سند تعریف شده توسط کاربر\nبا انتخاب هریک از انواع سند، اسناد با نوع انتخاب شده در گزارش شرکت می کنند.\n* سال مالی: از طریق فیلتر سال مالی می توانید محدوده سال های مالی مورد نظر برای اجرای گزارش را تعیین نمایید.\n* نوع مبلغ : در این فیلتر میتوانید مشخص کنید که چه نوع مبلغی را میخواهید مقایسه کنید که شامل موارد زیر است:\n+ مانده : با انتخاب مانده ، مانده های حساب در بازه انتخابی در گزارش نمایش داده میشود.\n+ گردش بدهکار: با انتخاب این مورد گردش بدهکار در بازه انتخابی نمایش داده میشود.\n+ گردش بستانکار: با انتخاب این مورد گردش بستانکار در بازه انتخابی نمایش داده میشود.\n* فیلترهای بیشتر : در فیلتر های بیشتر میتوانید موارد زیر را فیلتر کنید:\n+ ویژگی ارزی : با انتخاب این فیلتر معین های دارای ویژگی ارزی در گزارش نمایش داده میشود", "# انواع تفصیلی‌\nانواع تفصيل در سيستم به 3 دسته کلی تقسيم مي‌شوند:\n1. نوع تفصيل هايي كه جزو موجوديت هاي عمومي در سيستم هستند و برای همه ماژول‌ها استفاده می‌شوند و شامل موجوديت‌هاي ذیل می‌باشند.\n* شخص حقيقي / شخص حقوقي\n* مركز هزينه\n* پروژه\n* شعبه\n1. نوع تفصيل هايي كه ماژول مرتبط با آنها در سبد محصول وجود دارد. اين دسته از انواع تفصيل شامل دو بخش هستند:\n* ماژول مرتبط با آنها در قفل مشتري وجود دارد: در ماژول مرتبط، فرم معرفي نمونه موجوديت وجود دارد و بعد از ذخيره اوليه فرم، امكان تعريف اطلاعات تفصيل داده مي‌شود. مثل تسهیلات مالی\n* ماژول مرتبط در قفل مشتري وجود ندارد : در ماژول دفتر كل يك فرم با حداقل اطلاعات مورد نیاز بابت هر كدام از اين انواع تفصيل وجود دارد. برای مثال حساب بانکی، صندوق، تنخواه و ....\nدر اين فرم حداقل اطلاعاتي كه نمونه هاي اين موجوديت را معنی‌دار مي كند توسط كاربر ثبت شده و اطلاعات تفصيل مربوط به اين نمونه موجوديت هم مطابق با قواعد اطلاعات تفصيل در دفتر كل ثبت مي شود.\nاین نوع تفصیل‌ها در حال حاضر در سیستم شامل موارد ذیل است:\n* حساب بانکی\n* صندوق\n* تنخواه\n* کالا\n* حوزه قیمت‌گذاری\n* گروه مشتریان\n* گروه کالا و خدمت\n1. نوع تفصيل هاي مورد نياز مشتري كه اطلاعات هويت آنها در سبد محصول وجود ندارد. براي اين انواع تفصيل که تفصیل سایر نام دارند، 10 عدد در سیستم به صورت پیش فرض وجود دارد که کاربر می‌تواند با فعال کردن و تغییر عنوان به عنوان دلخواه مورد استفاده قرار دهد.\nاین انواع تفصیل در سیستم شامل تفصیل سایر 1 تا سایر 10 است.\nامکان معرفی نوع تفصیل به صورت دستی در سیستم وجود ندارد. کاربر اگر بخواهد نوع تفصیل جدید غیر از موارد سیستمی داشته باشد، می‌تواند از انواع تفصیل سایر که حداکثر 10 تا است، استفاده کند.\nاز مسیر منوی اصلی/ حسابداری مالی/ دفتر کل/ حساب‌ها/ نوع تفصیل امکان مشاهده فهرست کل انواع تفصیل موجود در سیستم وجود دارد.\nبا قرار گرفتن روی هر ردیف و کلیک روی عنوان تفصیل می‌توان فهرست حساب‌های تفصیلی هر نوع تفصیل را مشاهده کرد.\nدر صورت وجود حساب تفصیل، امکان حذف نوع تفصیل وجود نخواهد داشت اما همواره برای جلوگیری از استفاده، می‌توانید نوع تفصیل را غیر فعال کنید.\n"]]
    mock_is_uniform.assert_called_once_with(expected_frequencies)
    
    # Check the call to _handle_clarification_case
    call_args = mock_handle_clarify.call_args[0]
    assert call_args[0] == mock_context
    assert set(call_args[1]) == {'دفتر کل', 'مدیریت ارتباط با مشتری', 'انبار', 'فروش'} # Check list as set for order
    assert call_args[2] == expected_proposable
    
    mock_handle_single.assert_not_called()
    mock_handle_clear.assert_not_called()


### test hash string

@pytest.mark.parametrize("input_string, expected_hash", [
    # Test case 1: A standard ASCII string
    (
        "چطوری معین ایجاد کنم",
        "a75c88226ded2c5ffa36c1d8a89bab27b3e2e6e0477b1ab40d4d8c125df4075e"
    ),
    
    # Test case 2: An empty string
    (
        "",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    ),
    
    # Test case 3: A string with Unicode characters (Farsi/Persian)
    (
        "سلام",
        "bda1fa48345336618741fd2c4bc02809eb099c49a9b02fb5056401ab6d4dc3e6"
    ),
    
    # Test case 4: A simple word
    (
        "pytest",
        "2b01214d32c382dbc73bf6b493bedb7926324af27bad3ee888f66774b9b114c8"
    )
])
def test_hash_string_known_values(input_string, expected_hash):
    """
    Tests the hash_string function against a set of known, pre-computed
    SHA-256 hashes to ensure it is working correctly.
    """
    # 1. Arrange
    # (Input is provided by @pytest.mark.parametrize)
    
    # 2. Act
    result = hash_string(input_string)
    
    # 3. Assert
    assert result == expected_hash

### test _handle_single_module

def test_handle_single_module_case_with_context():
    """
    Tests the function with a standard list of context items.
    """
    # 1. Arrange
    mock_context = [{"text": "# قلم سند انبار\nدر سیستم انبار، برای مشاهده اطلاعات کلیه ی اقلام اسناد ورودی و خروجی کالا به انبار، از فرم قلم سند انبار استفاده می شود. این اطلاعات به عنوان مبنایی برای کنترل موجودی، تهیه گزارشات و تصمیم‌گیری‌های مرتبط با انبار استفاده می‌شوند.\n\n## فهرست قلم سند انبار\n## صفحه مشاهده اقلام سند انبار", "index": 32, "module": "انبار", "source": "inventory.csv"}, {"text": "# اسناد تجمیعی\nدر سیستم انبار، اسناد تجمیعی انبار به اسنادی گفته می‌شود که چندین اقلام سند انبار با جزئیات مختلف را در یک سند واحد جمع‌آوری می‌کنند. این نوع اسناد، برای ساده‌سازی فرآیندهای انبار و حسابداری، کاهش خطای انسانی و بهبود دقت در گزارش‌گیری از انبار مورد استفاده قرار می‌گیرند. اسناد تجمیعی به کاربر این امکان را می دهد تا بتواند با انتخاب سند درخواست کالا، بر مبنای آن سند انبار ثبت نماید. همچنین کاربر می تواند با انتخاب کالاهای تعریف شده، سند انبار ثبت نماید، با این کار کالاهای انتخاب شده در لیست اقلام سند قرار می گیرد.\n\n## فهرست اسناد تجمیعی\n## مراحل ثبت اسناد تجمیعی", "index": 11, "module": "انبار", "source": "inventory.csv"}, {"text": "# قلم سند انبار\n## صفحه مشاهده اقلام سند انبار\nدر صورت انتخاب یک قلم سند انبار از فرم فهرست، فرم مشاهده سند انبار مربوط به آن قلم کالا با امکانات زیر نمایش داده می شود:\n1. نام شرکت: شرکتی را که در آن سند انبار ایجاد می کنیم نمایش می دهد.\n2. سال مالی: سال مالی شرکتی که در آن ثبت سند انجام می دهیم را نمایش داده می شود.\n3. وضعیت سند: این گزینه وضعیت سند را مشخص می کند که عبارت است از: تایید شده، ثبت شده و باطل شده\n4. وضعیت مبلغی سند: این گزینه وضعیت نرخ دهی سند انبار را نمایش می دهد.\n5. وضعیت صدور سند حسابداری: این گزینه نشان میدهد سند حسابداری برای سند خرید داخلی صادر شده است یا نه، اگر سند حسابداری صادر نشده باشد، وضعیت سند \"حسابداری نشده\" و اگر سند حسابداری برای سند انبار مربوطه صادر شده باشد، وضعیت سند \"حسابداری شده\" خواهد بود.\n6. ذخیره: این گزینه در این حالت غیر فعال می باشد. اگر وضعیت سند در حالت ثبت شده باشد، با تغییر اطلاعات فیلدهای سند (فیلدهای سربرگ و اقلام سند (این گزینه برای کاربر فعال می شود.\n7. تغییر وضعیت: اولین وضعیت یک سند ثبت شده می باشد و برای تایید آن یا برای برگشت از تایید از گزینه تغییر وضعیت استفاده می شود. همچنین امکان ابطال سند مربوطه نیز وجود دارد.\n8. چاپ: از گزینه چاپ برای چاپ سند انبار استفاده می شود. برای چاپ سند انبار یک الگوی پیش فرض وجود دارد و در صورت داشتن دسترسی می توان الگوهای آن را تغییر داده و با عنوان الگوی چاپ جدید ذخیره نمود.\n9. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم سند انبار را فراهم می کند.\n10. کپی: با استفاده از این گزینه می توان از روی سند انبار مربوطه، یک سند انبار دیگری با الگوی مشابه به همراه اطلاعات درج شده در فیلدهای سربرگ و اقلام سند انبار در تب جدید ایجاد کرد.\n11. حذف: این گزینه امکان حذف سند انبار ثبت شده در سیستم را به کاربر می دهد. اگر سند تایید شده و یا ابطال شده باشد، نمی توان آن را حذف کرد.\n12. سایر عملیات: این گزینه امکان ایجاد سند انبار جدید و نمایش فهرست سند انبار را فراهم می سازد.\n", "index": 15, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. این گزینه به عنوان تسهیلات کاربری استفاده می شود برای اینکه در صورتی که کاربر نیاز به رسید یا حواله اجزای یک کالای کلی داشته باشد به جای اینکه همه ان اجزا را در فرم سند انبار انتخاب نماید، کالای اصلی و کلی را انتخاب کرده و خود سیستم با توجه به فرمول انتخابی اجزای کالا را به کاربر نمایش دهد . در این حالیت انباردار می تواند در صورت نیاز مقادیر آنرا نیز ویرایش نماید. این گزینه صرفا تسهیلات کاربری بوده و تغییری در موجودی کالای اصلی بوجود نمی اید. با این امکان در زمان ثبت اسناد صرفه جویی شده و اشتباهات کاربری ناشی از فراموشی انتخاب یکی از اجزای کالا کاهش می باشد.\nدر بخش سایدبار سند انبار جمع کل اقلام سند به واحدهای ثبت سند، واحد اصلی و واحد دوم نمایش داده می شود.\nدر صورتی که سند انبار دارای اسناد مرتبط باشد نیز **پس از ذخیره سند** در بخش سایدبار نمایش داده می شود.\nدر صورتی که یکی از ردیف های سند انبار انتخاب گردد، در قسمت ساید بار مشخصات تکمیلی کالا شامل طبقه حساب کالا، نوع کالا، نوع کارکرد کالا و ویژگی های سطح کالا نمایش داده می شود", "index": 5, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- صدور هوشمند سند\nبرای ثبت سند انبار از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه صدور هوشمند سند، را انتخاب نمایید.\nدر این حالت فرمی جهت انتخاب فاکتور چاپی به کاربر نمایش داده می شود. انباردار فاکتور چاپی را از طریق گزینه بارگذاری تصویر انتخاب کرده سپس گزینه بارگذاری کلیک می نماید. پس از انتخاب گزینه بارگذاری، یک عملیات برای شناسایی ایتم های فاکتور اجرا می شود. در صورتی که اجرای عملیات و شناسایی و خواندن فاکتور چاپی با موفقیت انجام شود پیامی مبنی بر اجرای موفق آن به کاربر نمایش داده شده و با بستن فرم اجرای عملیات، فرم مشاهده موارد شناسایی شده و اصلاح موارد مورد نیاز به کاربر نمایش داده می شود.\nدر صورتی که به هر دلیل اجرای عملیات ناموفق باشد و خواندن ایتمهای فاکتور با مشکل مواجه شود، پیامی مبنی بر اجرای ناموفق عملیات به کاربر نماش داده می شود.\n", "index": 9, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### فهرست الگوی سند انبار\nدر صفحه ی فهرست الگوی سند انبار می توان لیستی از الگوهای اسناد انبار تعریف شده در سیستم را مشاهده کرد. ستون های قابل نمایش در فهرست سند انبار عبارتند از کد الگو، عنوان، جهت سند، نوع سند، نوع تاثیر بر سند، نوع طرف مقابل و وضعیت می باشد.\nبرای مشاهده­ی لیست سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، الگوی سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست الگوی سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست الگوی سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست الگوهای اسناد انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2", "index": 7, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\nبرای ثبت سند انبار از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای ثبت سند انبار ابتدا لازم است شرکت و الگوی مناسب برای ثبت سند اتخاب شود. در صورتی که الگو و شرکت انتخابی برای کاربر، جزو موارد پرکاربرد برای کاربر است، کاربر می تواند افزودن به منو را انتخاب کرده و در این حالت یک منو با عنوان الگوهای سند منتخب به منو اضافه شده و در زیر آن الگوی انتخابی اضافه می گردد.\nبرای ثبت سند انبار فیلدهای زیر تکمیل می گردد:\nانبار: نام انباری است که کالای خریداری شده لازم است در آن رسید گردد، انتخاب شود. انتخاب انبار اجباری است. در این لیست تنها انبارهایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد انبار نمایش داده می شود :\n* انبار متعلق به شرکت انتخابی باشد.\n* انبار فعال باشد.\n* الگوی انتخابی در لیست الگوهای مجاز آن انبارهای باشد.\nطرف مقابل: لیست همه طرف مقابل ها با توجه به الگوی انتخابی و تنظیمات الگو نمایش داده می شود", "index": 1, "module": "انبار", "source": "inventory.csv"}, {"text": "# قلم سند انبار\n## فهرست قلم سند انبار\nدر صفحه ی فهرست اقلام سند انبار می توان لیستی از کالاها به همراه اطلاعات مربوط به اسناد مرتبط با آن کالاها را مشاهده کرد. ستون های قابل نمایش در فهرست اقلام سند انبار عبارتند از شماره سند، عنوان سند، نوع سند، عنوان انبار، تاریخ سند، کد کالا، عنوان کالا، واحد سنجش، مقدار، مقدار به واحد اصلی، مقدار به واحد دوم، وضعیت سند و توضیحات.\nبرای مشاهده­ی لیست اقلام سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، قلم سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست اقلام سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست اقلام سند انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2. نام شرکت: در این گزینه نام شرکت وجود دارد در شرکتهایی که به صورت گروه یا هلدینگ می باشند، با استفاده از این گزینه می توان در صورت داشتن دسترسی، شرکت مورد نظر خود را انتخاب کرد تا بتوان لیستی از اقلام سندهای انبار ثبت شده مختص آن شرکت مورد نظر را مشاهده کرد.\n3. سال مالی: در این گزینه سال مالی وجود دارد که وابسته به نام شرکت می باشد و با توجه به شرکت انتخابی، سالهای تعریف شده برای آن شرکت نمایش داده می شود.\nفیلتر: این گزینه به منظور نمایش / عدم نمایش بخش جستجو و فیلتر مورد استفاده قرار می گیرد.\n1. بارگذاری مجدد: گاهی نیاز است بعد از تغییر یا حذف و ایجاد یک سند یا فیلتر و جستجو، فهرست خود را بارگذاری مجدد نماییم.\n2. تنظیمات: شامل انتخاب ستون ها، مرتب سازی، گروه بندی و تجمیع فیلترها برای نمایش فهرست می باشد.\n3. کپی لینک نما: از این گزینه برای به اشتراک گذاری صفحه فهرست با فیلترهای جاری استفاده می شود.\n4. جستجو و فیلتر: در این بخش می توان ستون های مورد نظر خود را برای فیلتر کردن و جستجو میان داده های آن ستون انتخاب نمود.\n5. تنظیم کننده عرض ستون: تنظیم اتوماتیک عرض تمامی ستون های جدول فهرست از طریق این گزینه انجام می شود.\n", "index": 24, "module": "انبار", "source": "inventory.csv"}, {"text": "# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\nبرای تعریف الگوی سند انبار از الگوی ثبت سند انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای تعریف الگوی سند انبار ابتدا لازم است از فهرست الگوهای استاندارد یکی از الگوها انتخاب شده و وارد فرم مشاهده و ویرایش آن شود.\nدر مشاهده الگوهای سند انبار 4 بخش زیر وجود دارد\n1. اطلاعات اصلی\n2. سایر طرف مقابل ها\n3. اطلاعات تکمیلی\n4. فیلدهای اضافه\nدر بخش اطلاعات اصلی فیلدهای زیر تکمیل می گردد:\n1. کد الگو که غیرقابل ویرایش است.\n2. عنوان الگو که عنوان پیشفرض نمایش داده شده و کاربر می تواند عنوان مورد نظر خود را وارد نماید.\n3. فیلدهای نوع سند، جهت سند، نوع خرید (در اسناد خرید) و نوع تاثیر بر موجودی غیرقابل تغییر بوده و در الگوها قرار گرفته است.\n4. تعداد اقلام سند، تعداد مجاز ردیف های سند انبار است که به صورت پیشفرض 200 ردیف بوده و حداکثر میتواند 500 رکورد باشد.\n5. فیلدهای اجباری و ویرایش درقلم می تواند برای طرف مقابل برای استفاده از امکان تغییر طرف مقابل در اقلام سند انبار استفاده شود.\n6", "index": 4, "module": "انبار", "source": "inventory.csv"}, {"text": "# سند انبار سند انبار\n### فهرست سند انبار\nدر صفحه ی فهرست سند انبار می توان لیستی از اسناد انبار تعریف شده در سیستم را مشاهده کرد. ستون های قابل نمایش در فهرست سند انبار عبارتند از شماره سند، الگوی سند، نوع سند، انبار، تاریخ، وضعیت سند، وضعیت قیمت گذاری، وضعیت سند حسابداری و توضیحات.\nبرای مشاهده­ی لیست سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست سند انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2", "index": 0, "module": "انبار", "source": "inventory.csv"}]
    mock_module = 'انبار'
    
    expected_documents = "# قلم سند انبار\nدر سیستم انبار، برای مشاهده اطلاعات کلیه ی اقلام اسناد ورودی و خروجی کالا به انبار، از فرم قلم سند انبار استفاده می شود. این اطلاعات به عنوان مبنایی برای کنترل موجودی، تهیه گزارشات و تصمیم‌گیری‌های مرتبط با انبار استفاده می‌شوند.\n\n## فهرست قلم سند انبار\n## صفحه مشاهده اقلام سند انبار\n\n# اسناد تجمیعی\nدر سیستم انبار، اسناد تجمیعی انبار به اسنادی گفته می‌شود که چندین اقلام سند انبار با جزئیات مختلف را در یک سند واحد جمع‌آوری می‌کنند. این نوع اسناد، برای ساده‌سازی فرآیندهای انبار و حسابداری، کاهش خطای انسانی و بهبود دقت در گزارش‌گیری از انبار مورد استفاده قرار می‌گیرند. اسناد تجمیعی به کاربر این امکان را می دهد تا بتواند با انتخاب سند درخواست کالا، بر مبنای آن سند انبار ثبت نماید. همچنین کاربر می تواند با انتخاب کالاهای تعریف شده، سند انبار ثبت نماید، با این کار کالاهای انتخاب شده در لیست اقلام سند قرار می گیرد.\n\n## فهرست اسناد تجمیعی\n## مراحل ثبت اسناد تجمیعی\n\n# قلم سند انبار\n## صفحه مشاهده اقلام سند انبار\nدر صورت انتخاب یک قلم سند انبار از فرم فهرست، فرم مشاهده سند انبار مربوط به آن قلم کالا با امکانات زیر نمایش داده می شود:\n1. نام شرکت: شرکتی را که در آن سند انبار ایجاد می کنیم نمایش می دهد.\n2. سال مالی: سال مالی شرکتی که در آن ثبت سند انجام می دهیم را نمایش داده می شود.\n3. وضعیت سند: این گزینه وضعیت سند را مشخص می کند که عبارت است از: تایید شده، ثبت شده و باطل شده\n4. وضعیت مبلغی سند: این گزینه وضعیت نرخ دهی سند انبار را نمایش می دهد.\n5. وضعیت صدور سند حسابداری: این گزینه نشان میدهد سند حسابداری برای سند خرید داخلی صادر شده است یا نه، اگر سند حسابداری صادر نشده باشد، وضعیت سند \"حسابداری نشده\" و اگر سند حسابداری برای سند انبار مربوطه صادر شده باشد، وضعیت سند \"حسابداری شده\" خواهد بود.\n6. ذخیره: این گزینه در این حالت غیر فعال می باشد. اگر وضعیت سند در حالت ثبت شده باشد، با تغییر اطلاعات فیلدهای سند (فیلدهای سربرگ و اقلام سند (این گزینه برای کاربر فعال می شود.\n7. تغییر وضعیت: اولین وضعیت یک سند ثبت شده می باشد و برای تایید آن یا برای برگشت از تایید از گزینه تغییر وضعیت استفاده می شود. همچنین امکان ابطال سند مربوطه نیز وجود دارد.\n8. چاپ: از گزینه چاپ برای چاپ سند انبار استفاده می شود. برای چاپ سند انبار یک الگوی پیش فرض وجود دارد و در صورت داشتن دسترسی می توان الگوهای آن را تغییر داده و با عنوان الگوی چاپ جدید ذخیره نمود.\n9. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم سند انبار را فراهم می کند.\n10. کپی: با استفاده از این گزینه می توان از روی سند انبار مربوطه، یک سند انبار دیگری با الگوی مشابه به همراه اطلاعات درج شده در فیلدهای سربرگ و اقلام سند انبار در تب جدید ایجاد کرد.\n11. حذف: این گزینه امکان حذف سند انبار ثبت شده در سیستم را به کاربر می دهد. اگر سند تایید شده و یا ابطال شده باشد، نمی توان آن را حذف کرد.\n12. سایر عملیات: این گزینه امکان ایجاد سند انبار جدید و نمایش فهرست سند انبار را فراهم می سازد.\n\n\n# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\n. این گزینه به عنوان تسهیلات کاربری استفاده می شود برای اینکه در صورتی که کاربر نیاز به رسید یا حواله اجزای یک کالای کلی داشته باشد به جای اینکه همه ان اجزا را در فرم سند انبار انتخاب نماید، کالای اصلی و کلی را انتخاب کرده و خود سیستم با توجه به فرمول انتخابی اجزای کالا را به کاربر نمایش دهد . در این حالیت انباردار می تواند در صورت نیاز مقادیر آنرا نیز ویرایش نماید. این گزینه صرفا تسهیلات کاربری بوده و تغییری در موجودی کالای اصلی بوجود نمی اید. با این امکان در زمان ثبت اسناد صرفه جویی شده و اشتباهات کاربری ناشی از فراموشی انتخاب یکی از اجزای کالا کاهش می باشد.\nدر بخش سایدبار سند انبار جمع کل اقلام سند به واحدهای ثبت سند، واحد اصلی و واحد دوم نمایش داده می شود.\nدر صورتی که سند انبار دارای اسناد مرتبط باشد نیز **پس از ذخیره سند** در بخش سایدبار نمایش داده می شود.\nدر صورتی که یکی از ردیف های سند انبار انتخاب گردد، در قسمت ساید بار مشخصات تکمیلی کالا شامل طبقه حساب کالا، نوع کالا، نوع کارکرد کالا و ویژگی های سطح کالا نمایش داده می شود\n\n# سند انبار سند انبار\n### مراحل ثبت سند انبار- صدور هوشمند سند\nبرای ثبت سند انبار از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه صدور هوشمند سند، را انتخاب نمایید.\nدر این حالت فرمی جهت انتخاب فاکتور چاپی به کاربر نمایش داده می شود. انباردار فاکتور چاپی را از طریق گزینه بارگذاری تصویر انتخاب کرده سپس گزینه بارگذاری کلیک می نماید. پس از انتخاب گزینه بارگذاری، یک عملیات برای شناسایی ایتم های فاکتور اجرا می شود. در صورتی که اجرای عملیات و شناسایی و خواندن فاکتور چاپی با موفقیت انجام شود پیامی مبنی بر اجرای موفق آن به کاربر نمایش داده شده و با بستن فرم اجرای عملیات، فرم مشاهده موارد شناسایی شده و اصلاح موارد مورد نیاز به کاربر نمایش داده می شود.\nدر صورتی که به هر دلیل اجرای عملیات ناموفق باشد و خواندن ایتمهای فاکتور با مشکل مواجه شود، پیامی مبنی بر اجرای ناموفق عملیات به کاربر نماش داده می شود.\n\n\n# الگوی سند انبار\n### فهرست الگوی سند انبار\nدر صفحه ی فهرست الگوی سند انبار می توان لیستی از الگوهای اسناد انبار تعریف شده در سیستم را مشاهده کرد. ستون های قابل نمایش در فهرست سند انبار عبارتند از کد الگو، عنوان، جهت سند، نوع سند، نوع تاثیر بر سند، نوع طرف مقابل و وضعیت می باشد.\nبرای مشاهده­ی لیست سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، الگوی سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست الگوی سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست الگوی سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست الگوهای اسناد انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2\n\n# سند انبار سند انبار\n### مراحل ثبت سند انبار- جدید\nبرای ثبت سند انبار از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای ثبت سند انبار ابتدا لازم است شرکت و الگوی مناسب برای ثبت سند اتخاب شود. در صورتی که الگو و شرکت انتخابی برای کاربر، جزو موارد پرکاربرد برای کاربر است، کاربر می تواند افزودن به منو را انتخاب کرده و در این حالت یک منو با عنوان الگوهای سند منتخب به منو اضافه شده و در زیر آن الگوی انتخابی اضافه می گردد.\nبرای ثبت سند انبار فیلدهای زیر تکمیل می گردد:\nانبار: نام انباری است که کالای خریداری شده لازم است در آن رسید گردد، انتخاب شود. انتخاب انبار اجباری است. در این لیست تنها انبارهایی نمایش داده می شود که دارای شرایط زیر باشد، در صورتی که یکی از این شرایط برقرار باشد انبار نمایش داده می شود :\n* انبار متعلق به شرکت انتخابی باشد.\n* انبار فعال باشد.\n* الگوی انتخابی در لیست الگوهای مجاز آن انبارهای باشد.\nطرف مقابل: لیست همه طرف مقابل ها با توجه به الگوی انتخابی و تنظیمات الگو نمایش داده می شود\n\n# قلم سند انبار\n## فهرست قلم سند انبار\nدر صفحه ی فهرست اقلام سند انبار می توان لیستی از کالاها به همراه اطلاعات مربوط به اسناد مرتبط با آن کالاها را مشاهده کرد. ستون های قابل نمایش در فهرست اقلام سند انبار عبارتند از شماره سند، عنوان سند، نوع سند، عنوان انبار، تاریخ سند، کد کالا، عنوان کالا، واحد سنجش، مقدار، مقدار به واحد اصلی، مقدار به واحد دوم، وضعیت سند و توضیحات.\nبرای مشاهده­ی لیست اقلام سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، قلم سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست اقلام سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست اقلام سند انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2. نام شرکت: در این گزینه نام شرکت وجود دارد در شرکتهایی که به صورت گروه یا هلدینگ می باشند، با استفاده از این گزینه می توان در صورت داشتن دسترسی، شرکت مورد نظر خود را انتخاب کرد تا بتوان لیستی از اقلام سندهای انبار ثبت شده مختص آن شرکت مورد نظر را مشاهده کرد.\n3. سال مالی: در این گزینه سال مالی وجود دارد که وابسته به نام شرکت می باشد و با توجه به شرکت انتخابی، سالهای تعریف شده برای آن شرکت نمایش داده می شود.\nفیلتر: این گزینه به منظور نمایش / عدم نمایش بخش جستجو و فیلتر مورد استفاده قرار می گیرد.\n1. بارگذاری مجدد: گاهی نیاز است بعد از تغییر یا حذف و ایجاد یک سند یا فیلتر و جستجو، فهرست خود را بارگذاری مجدد نماییم.\n2. تنظیمات: شامل انتخاب ستون ها، مرتب سازی، گروه بندی و تجمیع فیلترها برای نمایش فهرست می باشد.\n3. کپی لینک نما: از این گزینه برای به اشتراک گذاری صفحه فهرست با فیلترهای جاری استفاده می شود.\n4. جستجو و فیلتر: در این بخش می توان ستون های مورد نظر خود را برای فیلتر کردن و جستجو میان داده های آن ستون انتخاب نمود.\n5. تنظیم کننده عرض ستون: تنظیم اتوماتیک عرض تمامی ستون های جدول فهرست از طریق این گزینه انجام می شود.\n\n\n# الگوی سند انبار\n### مراحل تعریف الگوی سند انبار\nبرای تعریف الگوی سند انبار از الگوی ثبت سند انبار در ماژول لجستیک، از منو انبار و حسابداری انبار، عملیات تعدادی، سند انبار، گزینه ثبت سند انبار (+) را انتخاب نمایید.\nبرای تعریف الگوی سند انبار ابتدا لازم است از فهرست الگوهای استاندارد یکی از الگوها انتخاب شده و وارد فرم مشاهده و ویرایش آن شود.\nدر مشاهده الگوهای سند انبار 4 بخش زیر وجود دارد\n1. اطلاعات اصلی\n2. سایر طرف مقابل ها\n3. اطلاعات تکمیلی\n4. فیلدهای اضافه\nدر بخش اطلاعات اصلی فیلدهای زیر تکمیل می گردد:\n1. کد الگو که غیرقابل ویرایش است.\n2. عنوان الگو که عنوان پیشفرض نمایش داده شده و کاربر می تواند عنوان مورد نظر خود را وارد نماید.\n3. فیلدهای نوع سند، جهت سند، نوع خرید (در اسناد خرید) و نوع تاثیر بر موجودی غیرقابل تغییر بوده و در الگوها قرار گرفته است.\n4. تعداد اقلام سند، تعداد مجاز ردیف های سند انبار است که به صورت پیشفرض 200 ردیف بوده و حداکثر میتواند 500 رکورد باشد.\n5. فیلدهای اجباری و ویرایش درقلم می تواند برای طرف مقابل برای استفاده از امکان تغییر طرف مقابل در اقلام سند انبار استفاده شود.\n6\n\n# سند انبار سند انبار\n### فهرست سند انبار\nدر صفحه ی فهرست سند انبار می توان لیستی از اسناد انبار تعریف شده در سیستم را مشاهده کرد. ستون های قابل نمایش در فهرست سند انبار عبارتند از شماره سند، الگوی سند، نوع سند، انبار، تاریخ، وضعیت سند، وضعیت قیمت گذاری، وضعیت سند حسابداری و توضیحات.\nبرای مشاهده­ی لیست سند انبار می­توان از منوی ماژول لجستیک، انبار و حسابداری انبار، عملیات تعدادی انبار، سند انبار را انتخاب نمایید.\nدر بالای صفحه فهرست سند انبار گزینه و امکانات زیر وجود دارد:\n1. فهرست سند انبار: با استفاده از این گزینه ی آبشاری می توان نماهای تعریف شده در سیستم را مشاهده کرده و تنظیمات نما را ذخیره و آن ها را مدیریت کرد. به صورت پیشفرض فهرست سند انبار نمایش داده می شود. در صورتی که کاربر نیاز داشته باشد، فیلدهای نمایش داده در فهرست، چیدمان ستون های فهرست و شرایط آنرا برای نیاز خودش ذخیره نماید از گزینه مدیریت نماها استفاده می کند.\n2"
    expected_result = (False, [mock_module], expected_documents)

    # 2. Act
    result = _handle_single_module_case(mock_context, mock_module)

    # 3. Assert
    assert result == expected_result

def test_handle_single_module_case_with_empty_context():
    """
    Tests the edge case where the context list is empty.
    """
    # 1. Arrange
    mock_context = []
    mock_module = "انبار"
    
    expected_documents = "" # .join on an empty list is ""
    expected_result = (False, [mock_module], expected_documents)

    # 2. Act
    result = _handle_single_module_case(mock_context, mock_module)

    # 3. Assert
    assert result == expected_result

def test_handle_single_module_case_with_single_context():
    """
    Tests the case where there is only one context item.
    """
    # 1. Arrange
    mock_context = [{'text': '# قیمت سند انبار\n## مشاهده قیمت سند انبار\n. همچنین امکان ابطال سند مربوطه نیز وجود دارد.\n8. چاپ: از گزینه چاپ برای چاپ سند انبار استفاده می شود. برای چاپ سند انبار یک الگوی پیش فرض وجود دارد و در صورت داشتن دسترسی می توان الگوهای آن را تغییر داده و با عنوان الگوی چاپ جدید ذخیره نمود.\n9. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم سند انبار را فراهم می کند.\n10. کپی: با استفاده از این گزینه می توان از روی سند انبار مربوطه، یک سند انبار دیگری با الگوی مشابه به همراه اطلاعات درج شده در فیلدهای سربرگ و اقلام سند انبار در تب جدید ایجاد کرد.\n11. حذف: این گزینه امکان حذف سند انبار ثبت شده در سیستم را به کاربر می دهد. اگر سند تایید شده و یا ابطال شده باشد، نمی توان آن را حذف کرد.\n12. سایر عملیات: این گزینه امکان ایجاد سند انبار جدید و نمایش فهرست سند انبار را فراهم می سازد. همچنین از طریق این گزینه می توان با استفاده از اکشن "ویرایش معین" معین این سند را تغییر داد. با انتخاب این معین جدید همه ردیف هایی که از معین قبلی استفاده کرده اند به معین جدید تغییر می یابد.\nبا انتخاب گزینه قیمت سند وارد فرم قیمت سند می شود', 'index': 28, 'module': 'انبار', 'source': 'inventory.csv'}]
    mock_module = 'انبار'
    
    expected_documents = '# قیمت سند انبار\n## مشاهده قیمت سند انبار\n. همچنین امکان ابطال سند مربوطه نیز وجود دارد.\n8. چاپ: از گزینه چاپ برای چاپ سند انبار استفاده می شود. برای چاپ سند انبار یک الگوی پیش فرض وجود دارد و در صورت داشتن دسترسی می توان الگوهای آن را تغییر داده و با عنوان الگوی چاپ جدید ذخیره نمود.\n9. بارگذاری مجدد: این گزینه امکان بارگذاری مجدد فرم سند انبار را فراهم می کند.\n10. کپی: با استفاده از این گزینه می توان از روی سند انبار مربوطه، یک سند انبار دیگری با الگوی مشابه به همراه اطلاعات درج شده در فیلدهای سربرگ و اقلام سند انبار در تب جدید ایجاد کرد.\n11. حذف: این گزینه امکان حذف سند انبار ثبت شده در سیستم را به کاربر می دهد. اگر سند تایید شده و یا ابطال شده باشد، نمی توان آن را حذف کرد.\n12. سایر عملیات: این گزینه امکان ایجاد سند انبار جدید و نمایش فهرست سند انبار را فراهم می سازد. همچنین از طریق این گزینه می توان با استفاده از اکشن "ویرایش معین" معین این سند را تغییر داد. با انتخاب این معین جدید همه ردیف هایی که از معین قبلی استفاده کرده اند به معین جدید تغییر می یابد.\nبا انتخاب گزینه قیمت سند وارد فرم قیمت سند می شود'
    
    expected_result = (False, [mock_module], expected_documents)

    # 2. Act
    result = _handle_single_module_case(mock_context, mock_module)

    # 3. Assert
    assert result == expected_result

@patch("src.logic.hash_string") # Patch the dependency
def test_get_chitchat_cache_key(mock_hash_string):
    """
    Tests that _get_chitchat_cache_key correctly calls hash_string
    and prepends the 'chitchat_' prefix to the result.
    """
    # 1. Arrange
    mock_utterance = 'چطوری سند انبار بزنم؟'
    mock_hash_value = '79c470f35ac7e8562788d99e97cdcf13dcc51490b0784dea2fc36f566aa9caaf'
    
    # Configure the mock to return our known hash value
    mock_hash_string.return_value = mock_hash_value
    
    expected_key = f"chitchat_{mock_hash_value}"

    # 2. Act
    result = _get_chitchat_cache_key(mock_utterance)

    # 3. Assert
    # Check that the final string is correct
    assert result == expected_key
    
    # Check that hash_string was called correctly
    mock_hash_string.assert_called_once_with(mock_utterance)

@patch("src.logic.hash_string")
def test_get_chitchat_cache_key_empty_string(mock_hash_string):
    """
    Tests the function with an empty string utterance.
    """
    # 1. Arrange
    mock_utterance = ""
    mock_hash_value = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # (Real hash for empty)
    
    mock_hash_string.return_value = mock_hash_value
    
    expected_key = f"chitchat_{mock_hash_value}"

    # 2. Act
    result = _get_chitchat_cache_key(mock_utterance)

    # 3. Assert
    assert result == expected_key
    mock_hash_string.assert_called_once_with(mock_utterance)

def test_handle_clear_preference_case_with_context():
    """
    Tests the function with a standard list of context items.
    """
    # 1. Arrange
    mock_context = [{"text": "# **رسید دریافت**\n## **اطلاعات اقلام رسید دریافت**\n.\n**سایر اطلاعات:** در صورتی که در الگوی سند دریافت وجه نقد، نمایش و تکمیل اطلاعات دیگر انتخاب شده باشد، در دریافت وجه نقد نمایش داده شده و قابل ثبت خواهند بود. برخی از این اطلاعات عبارت هستند از مالیات بر ارزش افزوده، اطلاعات تفصیل مانند طرف تجاری، مرکز هزینه، پروژه و ...، بابت، تحویل دهنده/گیرنده، شرح، حساب معین.\n* + 1. چک\n**ردیف (#):** شماره ترتیب اقلام را نشان می دهد که توسط سیستم و به ترتیب از شماره 1 تا شماره آخرین قلم ثبت می شود.\n**پرداخت کننده:** ابتدا نقش پرداخت کننده و سپس پرداخت کننده انتخاب می شود. پرداخت کننده هایی نمایش داده می شوند که دارای نقش انتخاب شده با وضعیت فعال باشند. همچنین در صورتی که ماژول حساب های دریافتنی (AR) وجود داشته باشد، فیلد حساب نمایش داده می شود. اگر نقش انتخابی برای پرداخت کننده، مشتری باشد، تکمیل فیلد حساب اجباری خواهد بود. با انتخاب حساب مشتری و بر اساس نوع سند و سناریوی حساب مشتری، تراکنش مربوطه در ماژول حساب های دریافتنی ثبت خواهد شد، تا در کنترل مانده حساب مشتری و آنالیز حساب مورد استفاده قرار بگیرد", "index": 39, "module": "خزانه داری", "source": "treasury.csv"}, {"text": "# فرآیند پیش از فروش\n### **2-5-4 فیلد های پیش فاکتور**\n.\n**روش تسویه**\nنوع روش پرداختی که برای این پیش‌فاکتور در نظر گرفته شده است (نقدی، چک، اعتباری و...). این فیلد در مدیریت نقدینگی و برنامه‌ریزی مالی نقش دارد.\n**تحویل‌گیرنده**\nشخص یا واحدی که کالا یا خدمات باید به او تحویل شود. در پیش‌فاکتورهای مرتبط با تحویل فیزیکی کالا، تعیین دقیق این فیلد ضروری است.\n**وضعیت**\nوضعیت جاری پیش‌فاکتور (مثلاً ثبت‌شده، تأیید شده و...). این فیلد برای تعیین مراحل اجرایی سند و اقدامات بعدی مورد استفاده قرار می‌گیرد.\n**مرحله پیش‌فاکتور**\nنشان‌دهنده موقعیت پیش‌فاکتور در فرآیند فروش (پیش‌نویس، ارسال‌شده، تأییدشده و...). این اطلاعات در پیگیری و مدیریت فرآیندهای فروش بسیار حائز اهمیت است.", "index": 7, "module": "مدیریت ارتباط با مشتری", "source": "crm.csv"}, {"text": "# **2- عملیات فروش**\n## **3-2 فاکتورهای برگشتی**\n. در غیر اینصورت نیازی به انتخاب کارمند فروش نیست.\nنکته: کارمندان فروشی در این لیست مشاده میشوند که با دفتر فروش فاکتور مرتبط شده باشند. اگر دفتر فروش انتخاب نشده باشد، کلیه کارمندان (اشخاصی که نقش کارمند دارند) در لیست مشاهده شده و میتوان از میان آنها یکی را انتخاب نمود.\n** دریافت کننده صورتحساب: از میان اشخاص حقیقی/حقوقی که به مشتری بعنوان دریافت کننده صورتحساب مرتبط شده اند یک دریافت کننده را انتخاب میکنیم. بصورت پیش فرض دریافت کننده صورتحساب همان مشتری است اما گاهی فاکتورهای برگشتی به شخص دیگری ارسال میشود بدین جهت میتوان دریافت کننده فاکتور برگشتی را شخصی غیر از مشتری انتخاب نمود.\n** ارز: ارزی که براساس آن توافق قیمتها با مشتری انجام شده از میان ارزهای مرتبط با انتخاب میشود. بصورت پیش فرض، ارز عملیاتی سیستم، در فاکتور پر شده است اما میتوان آنرا به ارز دیگری هم تغییر داد.\n** توضیحات: در صورت نیاز، میتوان توضیحاتی برای فاکتور برگشتی توسط کاربر ثبت نمود.\nپس از پر کردن اطلاعات اصلی، اقلام فاکتور برگشتی را ثبت می نماییم. به ازای هر کالا یا خدمت یک قلم در فاکتور برگشتی ثبت می نماییم", "index": 9, "module": "فروش", "source": "sales.csv"}, {"text": "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** شعبه: شعبه ی شرکت را انتخاب می نماییم.\n** شماره سند: شماره سفارش یا بصورت اتوماتیک اختصاص داده میشود یا کاربر باید آنرا وارد کند. در تعریف روش شماره گذاری، روشی که برای شماره گذاری سفارش تعریف شده تعیین کننده نحوه ثبت شماره خواهد بود.\n** روش تسویه: روش تسویه توافق شده با مشتری را در این قسمت از میان روش های تسویه تعریف شده انتخاب می نماییم.\n** تاریخ: تاریخی که سفارش باید به آن تاریخ صادر گردد را ثبت میکنیم.\n** تاریخ اعتبار: تاریخی که سفارش تا آن تاریخ اعتبار دارد را مشخص میکنیم.\n** دفتر فروش: در صورتیکه شرکتی بیش از یک دفتر فروش داشته باشد این دفتر فروش توسط کاربر صادرکننده سفارش انتخاب میشود. در غیر اینصورت نیازی به انتخاب دفتر فروش نیست.\n** کارمند فروش: در صورت نیاز به داشتن اطلاعات اینکه این فروش توسط چه کارشناس فروشی پیش برده شده، کارمند فروش را انتخاب می نماییم. در غیر اینصورت نیازی به انتخاب کارمند فروش نیست.\nنکته: کارمندان فروشی در این لیست مشاده میشوند که با دفتر فروش سفارش مرتبط شده باشند", "index": 3, "module": "فروش", "source": "sales.csv"}, {"text": "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n. اگر دفتر فروش انتخاب نشده باشد، کلیه کارمندان (اشخاصی که نقش کارمند دارند) در لیست مشاهده شده و میتوان از میان آنها یکی را انتخاب نمود.\n** توضیحات: در صورت نیاز، میتوان توضیحاتی برای سفارش توسط کاربر ثبت نمود.\n* در قسمت اطلاعات صورتحساب و پرداخت اطلاعات زیر را وارد می نماییم:\n** پرداخت کننده: از میان اشخاص حقیقی/حقوقی که به مشتری سفارش جاری، بعنوان پرداخت کننده مبلغ صورتحساب مرتبط شده اند یک پرداخت کننده را انتخاب میکنیم. بصورت پیش فرض پرداخت کننده صورتحساب همان مشتری است اما گاهی تسویه فاکتورهای یک شخص توسط شخص دیگری انجام میشود بدین جهت میتوان پرداخت کننده را شخصی غیر از مشتری انتخاب نمود.\n** دریافت کننده صورتحساب: از میان اشخاص حقیقی/حقوقی که به مشتری سفارش جاری، بعنوان دریافت کننده صورتحساب مرتبط شده اند یک دریافت کننده را انتخاب میکنیم. بصورت پیش فرض دریافت کننده صورتحساب همان مشتری است اما گاهی فاکتورها به شخص دیگری ارسال میشود بدین جهت میتوان دریافت کننده صورتحساب را شخصی غیر از مشتری انتخاب نمود", "index": 2, "module": "فروش", "source": "sales.csv"}, {"text": "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** نشانی تحویل: نشانی که قرار است کالا / خدمت در آن تحویل داده شود را از میان \"نشانی های مشتری که بعنوان نشانی تحویل تعریف شده است\"، انتخاب می نماییم.\n** توضیحات تحویل: در صورت نیاز به توضیحات اضافه، توضیحات تحویل را میتوان وارد نمود.\nنکته: اطلاعات تحویل در صورت نیاز، میتواند به ازای قلم های مختلف سفارش، متفاوت تعریف شود.\nپس از پر کردن اطلاعات اصلی سفارش، اقلام سفارش را ثبت می نماییم. به ازای هر کالا یا خدمت یک قلم در سفارش ثبت می نماییم. در ادامه نحوه ثبت اقلام را توضیح میدهیم:\n* ابتدا دکمه \"ایجاد\" را زده تا یک قلم جدید ایجاد شود.\n* قلم: در فیلد قلم، کالا یا خدمت مورد نظر را انتخاب می نماییم.\nنکته: در این لیست کالا/ خدمت هایی قابل مشاهده است که شرایط زیر را داشته باشد:\n** کلیه خدماتی که در شرکت تعریف شده و وضعیت فعال داشته باشند.\n** کالاهایی که کارکرد آن در شرکت جاری، قابل فروش بوده و وضعیت فعال داشته باشد. همچنین انبار مرتبط با کالا باید به حوزه فروش فاکتور جاری مرتبط شده باشد.\n* واحد سنجش: با انتخاب قلم مورد نظر (کالا یا خدمت)، با واحد سنجش پیش فرض کالا یا خدمت در قلم پر میشود", "index": 6, "module": "فروش", "source": "sales.csv"}, {"text": "# اطلاعات پایه\n## **2-1 مدیریت طرف تجاری**\n### **1-2-1 مشتری ها**\n. برای استفاده از مشتری موردی، یک مشتری حقیقی را بعنوان مشتری موردی تعریف کرده و در اسناد فروش (سفارش فروش- فاکتور فروش و فاکتور برگشتی) این مشتری را انتخاب کرده و اطلاعات شخصی که خریدار است را در همان سند وارد می نماییم.\nطرف های تجاری:\nپرداخت کننده: به ازای هر مشتری مشخص می نماییم چه کسی پرداخت کننده وجوه صورتحساب های این مشتری خواهد بود.\nتحویل گیرنده: به ازای هر مشتری مشخص می نماییم چه کسی تحویل گیرنده کالا یا خدمات صورتحساب های این مشتری خواهد بود.\nدریافت کننده صورتحساب: به ازای هر مشتری مشخص می نماییم چه کسی دریافت کننده صورتحساب های این مشتری خواهد بود.\nگروه های عضو:\nدر صورت تعریف گروهبندی مشتری، میتوان از فرم تعریف مشتری، به ازای هر مشتری از میان گروهبندی های تعریف شده، مشتری را به گروه مشتری مدنظر تخصیص داد", "index": 13, "module": "فروش", "source": "sales.csv"}, {"text": "# **2- عملیات فروش**\n## **1-2 سفارش ها**\nسفارش فروش، سندی است که طی آن مشخص می کنیم چه مقدار از چه کالای یا خدمتی چه زمانی تحویل چه کسی شود. در سفارش فروش اطلاعاتی مشابه فاکتور ثبت میگردد.\nدر سیستم فروش برای صدور فاکتور از مسیر \"فروش داخلی- عملیات فروش- سفارش ها\" وارد میشویم. پس از فشردن دکمه \"جدید\" یک فرم سفارش جدید باز شده و می توانیم اقدام به صدور سفارش نماییم:\n* ابتدا شرکت و سال مالی که سفارش در آن باید ایجاد شود را در بالای فرم سفارش انتخاب میکنیم.\n* در قسمت اطلاعات اصلی اطلاعات زیر را وارد میکنیم:\n** مشتری: در این فیلد، کد و نام مشتریان را مشاهده کرده و مشتری که برای وی می خواهیم سفارش صادر نماییم را انتخاب میکنیم.\nدر صورتی که مشتری انتخابی، مشتری موردی باشد فیلد مشتری موردی در سفارش فعال شده و میتوان اطلاعات نام، نام خانوادگی، کدملی، تلفن و آدرس مشتری را در آن وارد نمود.\nنکته: در صورتیکه مشتری قبلا بعنوان مشتری موردی خریدی انجام داده باشد در لیست مشتری موردی قابل انتخاب خواهد بود.\n** حوزه فروش: از میان حوزه فروش هایی که برای شرکت تعریف شده است، حوزه ای که از آن فروش انجام میشود را انتخاب می نماییم", "index": 4, "module": "فروش", "source": "sales.csv"}, {"text": "# **2- عملیات فروش**\n## **2-2 فاکتورها**\n.\n** ارز: ارزی که براساس آن توافق قیمتها با مشتری انجام شده از میان ارزهای مرتبط با انتخاب میشود. بصورت پیش فرض، ارز عملیاتی سیستم، در فاکتور پر شده است اما میتوان آنرا به ارز دیگری هم تغییر داد.\n* در قسمت اطلاعات حمل فاکتور اطلاعات زیر را وارد می نماییم:\n** تحویل گیرنده: شخصی که قرار است کالا یا خدمت را به نمایندگی از مشتری تحویل بگیرد در این قسمت انتخاب می نماییم. در این قسمت کلیه اشخاصی که از تعریف مشتری جاری، بعنوان تحویل گیرنده انتخاب شده است قابل مشاهده هستند. بصورت پیش فرض، تحویل گیرنده همان مشتری است.\n** نشانی تحویل: نشانی که قرار است کالا / خدمت در آن تحویل داده شود را از میان \"نشانی های مشتری که بعنوان نشانی تحویل تعریف شده است\"، انتخاب می نماییم.\n** تاریخ تحویل: تاریخی که توافق شده در آن تاریخ کالا/خدمت به مشتری داده شود را وارد می نماییم.\n** زمان تحویل: ساعتی که توافق شده در آن ساعت کالا/خدمت به مشتری داده شود را وارد می نماییم.\n** توضیحات تحویل: در صورت نیاز به توضیحات اضافه، توضیحات تحویل را میتوان وارد نمود.\nپس از پر کردن اطلاعات اصلی فاکتور، اقلام فاکتور را ثبت می نماییم", "index": 1, "module": "فروش", "source": "sales.csv"}, {"text": "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** نشانی ارسال صورتحساب: از میان نشانی های ارسال صورتحساب، یک نشانی را انتخاب کرده تا سفارش جاری و صورتحساب آن به این نشانی ارسال شود.\nنکته: تنها نشانی هایی از مشتری در این فیلد قابل مشاهده است که در نشانی مشتری، تیک ارسال صورتحساب برای آن زده شده باشد.\n** ارز: ارزی که براساس آن توافق قیمتها با مشتری انجام شده از میان ارزهای مرتبط با انتخاب میشود. بصورت پیش فرض، ارز عملیاتی سیستم، در سفارش پر شده است اما میتوان آنرا به ارز دیگری هم تغییر داد.\n* در قسمت اطلاعات حمل سفارش اطلاعات زیر را وارد می نماییم:\n** تحویل گیرنده: شخصی که قرار است کالا یا خدمت را به نمایندگی از مشتری تحویل بگیرد در این قسمت انتخاب می نماییم. در این قسمت کلیه اشخاصی که از تعریف مشتری جاری، بعنوان تحویل گیرنده انتخاب شده است قابل مشاهده هستند. بصورت پیش فرض، تحویل گیرنده همان مشتری است.\n** تاریخ تحویل: تاریخی که توافق شده در آن تاریخ کالا/خدمت به مشتری داده شود را وارد می نماییم", "index": 0, "module": "فروش", "source": "sales.csv"}]
    mock_module = "فروش"
    
    expected_documents = ["# **رسید دریافت**\n## **اطلاعات اقلام رسید دریافت**\n.\n**سایر اطلاعات:** در صورتی که در الگوی سند دریافت وجه نقد، نمایش و تکمیل اطلاعات دیگر انتخاب شده باشد، در دریافت وجه نقد نمایش داده شده و قابل ثبت خواهند بود. برخی از این اطلاعات عبارت هستند از مالیات بر ارزش افزوده، اطلاعات تفصیل مانند طرف تجاری، مرکز هزینه، پروژه و ...، بابت، تحویل دهنده/گیرنده، شرح، حساب معین.\n* + 1. چک\n**ردیف (#):** شماره ترتیب اقلام را نشان می دهد که توسط سیستم و به ترتیب از شماره 1 تا شماره آخرین قلم ثبت می شود.\n**پرداخت کننده:** ابتدا نقش پرداخت کننده و سپس پرداخت کننده انتخاب می شود. پرداخت کننده هایی نمایش داده می شوند که دارای نقش انتخاب شده با وضعیت فعال باشند. همچنین در صورتی که ماژول حساب های دریافتنی (AR) وجود داشته باشد، فیلد حساب نمایش داده می شود. اگر نقش انتخابی برای پرداخت کننده، مشتری باشد، تکمیل فیلد حساب اجباری خواهد بود. با انتخاب حساب مشتری و بر اساس نوع سند و سناریوی حساب مشتری، تراکنش مربوطه در ماژول حساب های دریافتنی ثبت خواهد شد، تا در کنترل مانده حساب مشتری و آنالیز حساب مورد استفاده قرار بگیرد", "# فرآیند پیش از فروش\n### **2-5-4 فیلد های پیش فاکتور**\n.\n**روش تسویه**\nنوع روش پرداختی که برای این پیش‌فاکتور در نظر گرفته شده است (نقدی، چک، اعتباری و...). این فیلد در مدیریت نقدینگی و برنامه‌ریزی مالی نقش دارد.\n**تحویل‌گیرنده**\nشخص یا واحدی که کالا یا خدمات باید به او تحویل شود. در پیش‌فاکتورهای مرتبط با تحویل فیزیکی کالا، تعیین دقیق این فیلد ضروری است.\n**وضعیت**\nوضعیت جاری پیش‌فاکتور (مثلاً ثبت‌شده، تأیید شده و...). این فیلد برای تعیین مراحل اجرایی سند و اقدامات بعدی مورد استفاده قرار می‌گیرد.\n**مرحله پیش‌فاکتور**\nنشان‌دهنده موقعیت پیش‌فاکتور در فرآیند فروش (پیش‌نویس، ارسال‌شده، تأییدشده و...). این اطلاعات در پیگیری و مدیریت فرآیندهای فروش بسیار حائز اهمیت است.", "# **2- عملیات فروش**\n## **3-2 فاکتورهای برگشتی**\n. در غیر اینصورت نیازی به انتخاب کارمند فروش نیست.\nنکته: کارمندان فروشی در این لیست مشاده میشوند که با دفتر فروش فاکتور مرتبط شده باشند. اگر دفتر فروش انتخاب نشده باشد، کلیه کارمندان (اشخاصی که نقش کارمند دارند) در لیست مشاهده شده و میتوان از میان آنها یکی را انتخاب نمود.\n** دریافت کننده صورتحساب: از میان اشخاص حقیقی/حقوقی که به مشتری بعنوان دریافت کننده صورتحساب مرتبط شده اند یک دریافت کننده را انتخاب میکنیم. بصورت پیش فرض دریافت کننده صورتحساب همان مشتری است اما گاهی فاکتورهای برگشتی به شخص دیگری ارسال میشود بدین جهت میتوان دریافت کننده فاکتور برگشتی را شخصی غیر از مشتری انتخاب نمود.\n** ارز: ارزی که براساس آن توافق قیمتها با مشتری انجام شده از میان ارزهای مرتبط با انتخاب میشود. بصورت پیش فرض، ارز عملیاتی سیستم، در فاکتور پر شده است اما میتوان آنرا به ارز دیگری هم تغییر داد.\n** توضیحات: در صورت نیاز، میتوان توضیحاتی برای فاکتور برگشتی توسط کاربر ثبت نمود.\nپس از پر کردن اطلاعات اصلی، اقلام فاکتور برگشتی را ثبت می نماییم. به ازای هر کالا یا خدمت یک قلم در فاکتور برگشتی ثبت می نماییم", "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** شعبه: شعبه ی شرکت را انتخاب می نماییم.\n** شماره سند: شماره سفارش یا بصورت اتوماتیک اختصاص داده میشود یا کاربر باید آنرا وارد کند. در تعریف روش شماره گذاری، روشی که برای شماره گذاری سفارش تعریف شده تعیین کننده نحوه ثبت شماره خواهد بود.\n** روش تسویه: روش تسویه توافق شده با مشتری را در این قسمت از میان روش های تسویه تعریف شده انتخاب می نماییم.\n** تاریخ: تاریخی که سفارش باید به آن تاریخ صادر گردد را ثبت میکنیم.\n** تاریخ اعتبار: تاریخی که سفارش تا آن تاریخ اعتبار دارد را مشخص میکنیم.\n** دفتر فروش: در صورتیکه شرکتی بیش از یک دفتر فروش داشته باشد این دفتر فروش توسط کاربر صادرکننده سفارش انتخاب میشود. در غیر اینصورت نیازی به انتخاب دفتر فروش نیست.\n** کارمند فروش: در صورت نیاز به داشتن اطلاعات اینکه این فروش توسط چه کارشناس فروشی پیش برده شده، کارمند فروش را انتخاب می نماییم. در غیر اینصورت نیازی به انتخاب کارمند فروش نیست.\nنکته: کارمندان فروشی در این لیست مشاده میشوند که با دفتر فروش سفارش مرتبط شده باشند", "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n. اگر دفتر فروش انتخاب نشده باشد، کلیه کارمندان (اشخاصی که نقش کارمند دارند) در لیست مشاهده شده و میتوان از میان آنها یکی را انتخاب نمود.\n** توضیحات: در صورت نیاز، میتوان توضیحاتی برای سفارش توسط کاربر ثبت نمود.\n* در قسمت اطلاعات صورتحساب و پرداخت اطلاعات زیر را وارد می نماییم:\n** پرداخت کننده: از میان اشخاص حقیقی/حقوقی که به مشتری سفارش جاری، بعنوان پرداخت کننده مبلغ صورتحساب مرتبط شده اند یک پرداخت کننده را انتخاب میکنیم. بصورت پیش فرض پرداخت کننده صورتحساب همان مشتری است اما گاهی تسویه فاکتورهای یک شخص توسط شخص دیگری انجام میشود بدین جهت میتوان پرداخت کننده را شخصی غیر از مشتری انتخاب نمود.\n** دریافت کننده صورتحساب: از میان اشخاص حقیقی/حقوقی که به مشتری سفارش جاری، بعنوان دریافت کننده صورتحساب مرتبط شده اند یک دریافت کننده را انتخاب میکنیم. بصورت پیش فرض دریافت کننده صورتحساب همان مشتری است اما گاهی فاکتورها به شخص دیگری ارسال میشود بدین جهت میتوان دریافت کننده صورتحساب را شخصی غیر از مشتری انتخاب نمود", "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** نشانی تحویل: نشانی که قرار است کالا / خدمت در آن تحویل داده شود را از میان \"نشانی های مشتری که بعنوان نشانی تحویل تعریف شده است\"، انتخاب می نماییم.\n** توضیحات تحویل: در صورت نیاز به توضیحات اضافه، توضیحات تحویل را میتوان وارد نمود.\nنکته: اطلاعات تحویل در صورت نیاز، میتواند به ازای قلم های مختلف سفارش، متفاوت تعریف شود.\nپس از پر کردن اطلاعات اصلی سفارش، اقلام سفارش را ثبت می نماییم. به ازای هر کالا یا خدمت یک قلم در سفارش ثبت می نماییم. در ادامه نحوه ثبت اقلام را توضیح میدهیم:\n* ابتدا دکمه \"ایجاد\" را زده تا یک قلم جدید ایجاد شود.\n* قلم: در فیلد قلم، کالا یا خدمت مورد نظر را انتخاب می نماییم.\nنکته: در این لیست کالا/ خدمت هایی قابل مشاهده است که شرایط زیر را داشته باشد:\n** کلیه خدماتی که در شرکت تعریف شده و وضعیت فعال داشته باشند.\n** کالاهایی که کارکرد آن در شرکت جاری، قابل فروش بوده و وضعیت فعال داشته باشد. همچنین انبار مرتبط با کالا باید به حوزه فروش فاکتور جاری مرتبط شده باشد.\n* واحد سنجش: با انتخاب قلم مورد نظر (کالا یا خدمت)، با واحد سنجش پیش فرض کالا یا خدمت در قلم پر میشود", "# اطلاعات پایه\n## **2-1 مدیریت طرف تجاری**\n### **1-2-1 مشتری ها**\n. برای استفاده از مشتری موردی، یک مشتری حقیقی را بعنوان مشتری موردی تعریف کرده و در اسناد فروش (سفارش فروش- فاکتور فروش و فاکتور برگشتی) این مشتری را انتخاب کرده و اطلاعات شخصی که خریدار است را در همان سند وارد می نماییم.\nطرف های تجاری:\nپرداخت کننده: به ازای هر مشتری مشخص می نماییم چه کسی پرداخت کننده وجوه صورتحساب های این مشتری خواهد بود.\nتحویل گیرنده: به ازای هر مشتری مشخص می نماییم چه کسی تحویل گیرنده کالا یا خدمات صورتحساب های این مشتری خواهد بود.\nدریافت کننده صورتحساب: به ازای هر مشتری مشخص می نماییم چه کسی دریافت کننده صورتحساب های این مشتری خواهد بود.\nگروه های عضو:\nدر صورت تعریف گروهبندی مشتری، میتوان از فرم تعریف مشتری، به ازای هر مشتری از میان گروهبندی های تعریف شده، مشتری را به گروه مشتری مدنظر تخصیص داد", "# **2- عملیات فروش**\n## **1-2 سفارش ها**\nسفارش فروش، سندی است که طی آن مشخص می کنیم چه مقدار از چه کالای یا خدمتی چه زمانی تحویل چه کسی شود. در سفارش فروش اطلاعاتی مشابه فاکتور ثبت میگردد.\nدر سیستم فروش برای صدور فاکتور از مسیر \"فروش داخلی- عملیات فروش- سفارش ها\" وارد میشویم. پس از فشردن دکمه \"جدید\" یک فرم سفارش جدید باز شده و می توانیم اقدام به صدور سفارش نماییم:\n* ابتدا شرکت و سال مالی که سفارش در آن باید ایجاد شود را در بالای فرم سفارش انتخاب میکنیم.\n* در قسمت اطلاعات اصلی اطلاعات زیر را وارد میکنیم:\n** مشتری: در این فیلد، کد و نام مشتریان را مشاهده کرده و مشتری که برای وی می خواهیم سفارش صادر نماییم را انتخاب میکنیم.\nدر صورتی که مشتری انتخابی، مشتری موردی باشد فیلد مشتری موردی در سفارش فعال شده و میتوان اطلاعات نام، نام خانوادگی، کدملی، تلفن و آدرس مشتری را در آن وارد نمود.\nنکته: در صورتیکه مشتری قبلا بعنوان مشتری موردی خریدی انجام داده باشد در لیست مشتری موردی قابل انتخاب خواهد بود.\n** حوزه فروش: از میان حوزه فروش هایی که برای شرکت تعریف شده است، حوزه ای که از آن فروش انجام میشود را انتخاب می نماییم", "# **2- عملیات فروش**\n## **2-2 فاکتورها**\n.\n** ارز: ارزی که براساس آن توافق قیمتها با مشتری انجام شده از میان ارزهای مرتبط با انتخاب میشود. بصورت پیش فرض، ارز عملیاتی سیستم، در فاکتور پر شده است اما میتوان آنرا به ارز دیگری هم تغییر داد.\n* در قسمت اطلاعات حمل فاکتور اطلاعات زیر را وارد می نماییم:\n** تحویل گیرنده: شخصی که قرار است کالا یا خدمت را به نمایندگی از مشتری تحویل بگیرد در این قسمت انتخاب می نماییم. در این قسمت کلیه اشخاصی که از تعریف مشتری جاری، بعنوان تحویل گیرنده انتخاب شده است قابل مشاهده هستند. بصورت پیش فرض، تحویل گیرنده همان مشتری است.\n** نشانی تحویل: نشانی که قرار است کالا / خدمت در آن تحویل داده شود را از میان \"نشانی های مشتری که بعنوان نشانی تحویل تعریف شده است\"، انتخاب می نماییم.\n** تاریخ تحویل: تاریخی که توافق شده در آن تاریخ کالا/خدمت به مشتری داده شود را وارد می نماییم.\n** زمان تحویل: ساعتی که توافق شده در آن ساعت کالا/خدمت به مشتری داده شود را وارد می نماییم.\n** توضیحات تحویل: در صورت نیاز به توضیحات اضافه، توضیحات تحویل را میتوان وارد نمود.\nپس از پر کردن اطلاعات اصلی فاکتور، اقلام فاکتور را ثبت می نماییم", "# **2- عملیات فروش**\n## **1-2 سفارش ها**\n.\n** نشانی ارسال صورتحساب: از میان نشانی های ارسال صورتحساب، یک نشانی را انتخاب کرده تا سفارش جاری و صورتحساب آن به این نشانی ارسال شود.\nنکته: تنها نشانی هایی از مشتری در این فیلد قابل مشاهده است که در نشانی مشتری، تیک ارسال صورتحساب برای آن زده شده باشد.\n** ارز: ارزی که براساس آن توافق قیمتها با مشتری انجام شده از میان ارزهای مرتبط با انتخاب میشود. بصورت پیش فرض، ارز عملیاتی سیستم، در سفارش پر شده است اما میتوان آنرا به ارز دیگری هم تغییر داد.\n* در قسمت اطلاعات حمل سفارش اطلاعات زیر را وارد می نماییم:\n** تحویل گیرنده: شخصی که قرار است کالا یا خدمت را به نمایندگی از مشتری تحویل بگیرد در این قسمت انتخاب می نماییم. در این قسمت کلیه اشخاصی که از تعریف مشتری جاری، بعنوان تحویل گیرنده انتخاب شده است قابل مشاهده هستند. بصورت پیش فرض، تحویل گیرنده همان مشتری است.\n** تاریخ تحویل: تاریخی که توافق شده در آن تاریخ کالا/خدمت به مشتری داده شود را وارد می نماییم"]
    expected_result = (False, [mock_module], expected_documents)

    # 2. Act
    result = _handle_clear_preference_case(mock_context, mock_module)

    # 3. Assert
    assert result == expected_result

def test_handle_clear_preference_case_empty_context():
    """
    Tests the edge case where the context list is empty.
    """
    # 1. Arrange
    mock_context = []
    mock_module = "فروش"
    
    expected_documents = []  # The list comprehension will produce an empty list
    expected_result = (False, [mock_module], expected_documents)

    # 2. Act
    result = _handle_clear_preference_case(mock_context, mock_module)

    # 3. Assert
    assert result == expected_result

def test_handle_clear_preference_case_single_item():
    """
    Tests the case where there is only one item in the context list.
    """
    # 1. Arrange
    mock_context = [{"text": "# **رسید دریافت**\n## **اطلاعات اقلام رسید دریافت**\n.\n**سایر اطلاعات:** در صورتی که در الگوی سند دریافت وجه نقد، نمایش و تکمیل اطلاعات دیگر انتخاب شده باشد، در دریافت وجه نقد نمایش داده شده و قابل ثبت خواهند بود. برخی از این اطلاعات عبارت هستند از مالیات بر ارزش افزوده، اطلاعات تفصیل مانند طرف تجاری، مرکز هزینه، پروژه و ...، بابت، تحویل دهنده/گیرنده، شرح، حساب معین.\n* + 1. چک\n**ردیف (#):** شماره ترتیب اقلام را نشان می دهد که توسط سیستم و به ترتیب از شماره 1 تا شماره آخرین قلم ثبت می شود.\n**پرداخت کننده:** ابتدا نقش پرداخت کننده و سپس پرداخت کننده انتخاب می شود. پرداخت کننده هایی نمایش داده می شوند که دارای نقش انتخاب شده با وضعیت فعال باشند. همچنین در صورتی که ماژول حساب های دریافتنی (AR) وجود داشته باشد، فیلد حساب نمایش داده می شود. اگر نقش انتخابی برای پرداخت کننده، مشتری باشد، تکمیل فیلد حساب اجباری خواهد بود. با انتخاب حساب مشتری و بر اساس نوع سند و سناریوی حساب مشتری، تراکنش مربوطه در ماژول حساب های دریافتنی ثبت خواهد شد، تا در کنترل مانده حساب مشتری و آنالیز حساب مورد استفاده قرار بگیرد", "index": 39, "module": "خزانه داری", "source": "treasury.csv"}]
    mock_module = 'فروش'
    
    expected_documents = ["# **رسید دریافت**\n## **اطلاعات اقلام رسید دریافت**\n.\n**سایر اطلاعات:** در صورتی که در الگوی سند دریافت وجه نقد، نمایش و تکمیل اطلاعات دیگر انتخاب شده باشد، در دریافت وجه نقد نمایش داده شده و قابل ثبت خواهند بود. برخی از این اطلاعات عبارت هستند از مالیات بر ارزش افزوده، اطلاعات تفصیل مانند طرف تجاری، مرکز هزینه، پروژه و ...، بابت، تحویل دهنده/گیرنده، شرح، حساب معین.\n* + 1. چک\n**ردیف (#):** شماره ترتیب اقلام را نشان می دهد که توسط سیستم و به ترتیب از شماره 1 تا شماره آخرین قلم ثبت می شود.\n**پرداخت کننده:** ابتدا نقش پرداخت کننده و سپس پرداخت کننده انتخاب می شود. پرداخت کننده هایی نمایش داده می شوند که دارای نقش انتخاب شده با وضعیت فعال باشند. همچنین در صورتی که ماژول حساب های دریافتنی (AR) وجود داشته باشد، فیلد حساب نمایش داده می شود. اگر نقش انتخابی برای پرداخت کننده، مشتری باشد، تکمیل فیلد حساب اجباری خواهد بود. با انتخاب حساب مشتری و بر اساس نوع سند و سناریوی حساب مشتری، تراکنش مربوطه در ماژول حساب های دریافتنی ثبت خواهد شد، تا در کنترل مانده حساب مشتری و آنالیز حساب مورد استفاده قرار بگیرد"]
    
    expected_result = (False, ["فروش"], ["# **رسید دریافت**\n## **اطلاعات اقلام رسید دریافت**\n.\n**سایر اطلاعات:** در صورتی که در الگوی سند دریافت وجه نقد، نمایش و تکمیل اطلاعات دیگر انتخاب شده باشد، در دریافت وجه نقد نمایش داده شده و قابل ثبت خواهند بود. برخی از این اطلاعات عبارت هستند از مالیات بر ارزش افزوده، اطلاعات تفصیل مانند طرف تجاری، مرکز هزینه، پروژه و ...، بابت، تحویل دهنده/گیرنده، شرح، حساب معین.\n* + 1. چک\n**ردیف (#):** شماره ترتیب اقلام را نشان می دهد که توسط سیستم و به ترتیب از شماره 1 تا شماره آخرین قلم ثبت می شود.\n**پرداخت کننده:** ابتدا نقش پرداخت کننده و سپس پرداخت کننده انتخاب می شود. پرداخت کننده هایی نمایش داده می شوند که دارای نقش انتخاب شده با وضعیت فعال باشند. همچنین در صورتی که ماژول حساب های دریافتنی (AR) وجود داشته باشد، فیلد حساب نمایش داده می شود. اگر نقش انتخابی برای پرداخت کننده، مشتری باشد، تکمیل فیلد حساب اجباری خواهد بود. با انتخاب حساب مشتری و بر اساس نوع سند و سناریوی حساب مشتری، تراکنش مربوطه در ماژول حساب های دریافتنی ثبت خواهد شد، تا در کنترل مانده حساب مشتری و آنالیز حساب مورد استفاده قرار بگیرد"])

    # 2. Act
    result = _handle_clear_preference_case(mock_context, mock_module)

    # 3. Assert
    assert result == expected_result

### test _determine_final_route

# Mock config to be used in all tests
MOCK_CONFIG = {
    "router_model": {
        "address": "/home/jovyan/testing_units/Assistant-bot/saved_models/mlp.joblib",
        "model_name": "mlp",
        "beta_threshold": 0.3,
        "alpha_threshold" : 0.7
    },
    "embedding_model": {
        "model_name": "/home/jovyan/.cache/huggingface/hub/models--intfloat--multilingual-e5-large/snapshots/0dc5580a448e4284468b8909bae50fa925907bc5", 
        "device": "cuda"
    }
}

@pytest.mark.asyncio
@patch.dict("src.logic.config", MOCK_CONFIG)
@patch("src.logic._determine_final_route", new_callable=AsyncMock)
@patch("src.logic._get_chitchat_cache_key")
@patch("src.logic.SemanticRouterPipeline")
@patch("src.logic.Cache")
async def test_get_route_direct_cache_hit(
    mock_cache_class,
    mock_router_class,
    mock_get_chitchat_key,
    mock_determine_route
):
    """
    Tests Path 1: A direct route is found in the cache.
    """
    # 1. Arrange
    mock_utterance = 'بزرگترین محدودیتت چیه؟'
    expected_route = "chitchat"

    # Configure the Cache instance and its method
    mock_cache_instance = MagicMock()
    mock_cache_instance.get_exact_cache.return_value = "chitchat"
    mock_cache_class.return_value = mock_cache_instance

    # 2. Act
    result = await get_route_for_utterance(mock_utterance)

    # 3. Assert
    assert result == expected_route
    
    # Check that Cache was instantiated and get_exact_cache was called once
    mock_cache_class.assert_called_once_with()
    mock_cache_instance.get_exact_cache.assert_called_once_with(mock_utterance)

    # Ensure no other logic was executed
    mock_get_chitchat_key.assert_not_called()
    mock_router_class.assert_not_called()
    mock_determine_route.assert_not_called()

@pytest.mark.asyncio
@patch.dict("src.logic.config", MOCK_CONFIG)
@patch("src.logic._determine_final_route", new_callable=AsyncMock)
@patch("src.logic._get_chitchat_cache_key")
@patch("src.logic.SemanticRouterPipeline")
@patch("src.logic.Cache")
async def test_get_route_chitchat_cache_hit(
    mock_cache_class,
    mock_router_class,
    mock_get_chitchat_key,
    mock_determine_route
):
    """
    Tests Path 2: The direct cache misses, but the chitchat cache hits.
    """
    # 1. Arrange
    mock_utterance = 'بزرگترین محدودیتت چیه؟'
    mock_chitchat_key = "chitchat_e5473c7a0fbfe1e28fee6b5426ab7569c4b60bac194169fa50378fd3a9a69ad7"
    expected_route = "chitchat" # The constant CHITCHAT_ROUTE

    # Configure the Cache instance to miss first, then hit
    mock_cache_instance = MagicMock()
    mock_cache_instance.get_exact_cache.side_effect = [
        None,             # First call (direct cache) misses
        expected_route    # Second call (chitchat cache) hits
    ]
    mock_cache_class.return_value = mock_cache_instance
    
    # Configure the chitchat key helper
    mock_get_chitchat_key.return_value = mock_chitchat_key

    # 2. Act
    result = await get_route_for_utterance(mock_utterance)

    # 3. Assert
    assert result == expected_route
    
    # Check that the cache was called twice
    mock_cache_instance.get_exact_cache.assert_has_calls([
        call(mock_utterance),      # First call
        call(mock_chitchat_key)  # Second call
    ])
    
    # Check that the chitchat key helper was called
    mock_get_chitchat_key.assert_called_once_with(mock_utterance)

    # Ensure prediction logic was not executed
    mock_router_class.assert_not_called()
    mock_determine_route.assert_not_called()

@pytest.mark.asyncio
@patch.dict("src.logic.config", MOCK_CONFIG)
@patch("src.logic._determine_final_route", new_callable=AsyncMock)
@patch("src.logic._get_chitchat_cache_key")
@patch("src.logic.SemanticRouterPipeline")
@patch("src.logic.Cache")
async def test_get_route_cache_miss_full_prediction(
    mock_cache_class,
    mock_router_class,
    mock_get_chitchat_key,
    mock_determine_route
):
    """
    Tests Path 3: Both caches miss, forcing a full prediction.
    Also tests that the final result is stripped.
    """
    # 1. Arrange
    mock_utterance = 'بزرگترین محدودیتت چیه؟'
    mock_chitchat_key = "chitchat_e5473c7a0fbfe1e28fee6b5426ab7569c4b60bac194169fa50378fd3a9a69ad7"
    
    # --- Configure Cache (Path 3) ---
    mock_cache_instance = MagicMock()
    mock_cache_instance.get_exact_cache.return_value = None # Both calls miss
    mock_cache_class.return_value = mock_cache_instance
    
    mock_get_chitchat_key.return_value = mock_chitchat_key
    
    # --- Configure SemanticRouterPipeline (Path 3) ---
    mock_router_instance = MagicMock()
    # Define prediction results
    mock_predictions = ["chitchat"]
    mock_probabilities = [('chitchat', 0.979255072511712), ('illegal', 0.010473642182676953), ('irrelevant', 3.523722483614152e-05), ('qa', 0.010236034984353052), ('sql', 1.3096421759040971e-08)]
    mock_max_prob = 0.979255072511712
    mock_router_instance.predict_sentences.return_value = (
        mock_predictions, mock_probabilities, mock_max_prob
    )
    mock_router_class.return_value = mock_router_instance
    
    # --- Configure _determine_final_route (Path 3) ---
    mock_determine_route.return_value = "chitchat" # Note the spaces
    expected_route = "chitchat" # The stripped result

    # 2. Act
    result = await get_route_for_utterance(mock_utterance)

    # 3. Assert
    assert result == expected_route # Check that it was stripped
    
    # --- Verify all mocks were called correctly ---
    
    # Cache was checked twice
    mock_cache_instance.get_exact_cache.assert_has_calls([
        call(mock_utterance),
        call(mock_chitchat_key)
    ])
    
    # Router was instantiated with config values
    mock_router_class.assert_called_once_with(
        inference_only=True,
        embedding_address=MOCK_CONFIG["embedding_model"]["model_name"],
        classifier_address=MOCK_CONFIG["router_model"]["address"],
        model_name=MOCK_CONFIG["router_model"]["model_name"]
    )
    
    # Predict was called
    mock_router_instance.predict_sentences.assert_called_once_with([mock_utterance])
    
    # Final route determination was called
    mock_determine_route.assert_called_once_with(
        mock_utterance,
        mock_predictions[0],
        mock_probabilities,
        mock_max_prob
    )

# --- Test Cases ---
MOCK_CONFIG = {
    "router_model": {
        "address": "/home/jovyan/testing_units/Assistant-bot/saved_models/mlp.joblib",
        "model_name": "mlp",
        "beta_threshold": 0.3,
        "alpha_threshold" : 0.7
    },
    "embedding_model": {
        "model_name": "/home/jovyan/.cache/huggingface/hub/models--intfloat--multilingual-e5-large/snapshots/0dc5580a448e4284468b8909bae50fa925907bc5", 
        "device": "cuda"
    }
}

@pytest.mark.asyncio
@patch("src.logic.config", MOCK_CONFIG)
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
async def test_high_confidence_alpha_path_success(
    mock_get_chat_response: AsyncMock, 
):
    """
    Tests the primary success path:
    - High confidence (prob > alpha)
    - Not 'illegal'
    - Does not contain 'همکاران'
    - Should return top_prediction immediately.
    """
    # Arrange
    
    mock_utterance = 'بزرگترین محدودیتت چیه؟'
    mock_top_prediction = 'chitchat'
    mock_probabilities = [('chitchat', 0.979255072511712), ('illegal', 0.010473642182676953), ('irrelevant', 3.523722483614152e-05), ('qa', 0.010236034984353052), ('sql', 1.3096421759040971e-08)]
    mock_max_prob = 0.979255072511712

    # Act
    result = await _determine_final_route(
        mock_utterance, mock_top_prediction, mock_probabilities, mock_max_prob
    )

    # Assert
    assert result == "chitchat"
    mock_get_chat_response.assert_not_called()
    # Check that pdb.set_trace() was called (or just patch it away like here)
    # mock_pdb.set_trace.assert_called_once() # Uncomment if you want to check


@pytest.mark.asyncio
@patch("src.logic.config", MOCK_CONFIG)
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
async def test_high_confidence_but_contains_hamkaran( 
    mock_get_chat_response
):
    """
    Tests the path where confidence is high, but the utterance contains 'همکاران'.
    - Should bypass the alpha check.
    - Should build plausible_routes with *all* routes, ignoring beta.
    - Should call LLM with all routes.
    """
    
    mock_get_chat_response.return_value = "illegal" # Mocked LLM response
    
    mock_utterance = 'آدرس منزل یکی از اعضای هیئت مدیره همکاران سیستم را پیدا کن'
    mock_top_prediction = "illegal"
    # Note: 'illegal' (0.95) > beta (0.5), so plausible_routes = ['illegal']
    mock_probabilities =[('chitchat', 2.0396348276130513e-12), ('illegal', 0.999999058148231), ('irrelevant', 1.7368169709484596e-10), ('qa', 9.296892439143856e-07), ('sql', 1.1986803654295443e-08)]
    mock_max_prob = 0.999999058148231

    # Act
    result = await _determine_final_route(
        mock_utterance, mock_top_prediction, mock_probabilities, mock_max_prob
    )

    # Assert
    assert result == "illegal"
    
    # It should fail the alpha check (top_prediction == "illegal")
    # It should build plausible_routes = ['illegal'] (len < 2)
    # It should fall back to top 2: ['illegal', 'qa']
    expected_llm_routes = ['chitchat', 'illegal', 'irrelevant', 'qa', 'sql']
    expected_llm_call = SEMANTIC_ROUTER.format(user_query=mock_utterance, class_list=expected_llm_routes)
    
    mock_get_chat_response.assert_called_once_with(expected_llm_call)


@pytest.mark.asyncio
@patch("src.logic.config", MOCK_CONFIG)
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
async def test_high_confidence_but_illegal(
    mock_get_chat_response: AsyncMock
):
    """
    Tests the path where confidence is high, but the top prediction is 'illegal'.
    - Should bypass the alpha check and go to disambiguation.
    - Falls into the '< 2 plausible' logic, sorting and taking top 2.
    """
    # Arrange
    mock_get_chat_response.return_value = "illegal" # Mocked LLM response
    
    mock_utterance = 'نام کاربری و رمز عبور پورتال داخلی یکی از کارمندان را پیدا کن'
    mock_top_prediction = "illegal"
    mock_probabilities = [('chitchat', 1.1660619821375876e-11), ('illegal', 0.9999998866201905), ('irrelevant', 1.3208627223021756e-09), ('qa', 5.982179068980666e-08), ('sql', 5.222549538425229e-08)]
    mock_max_prob = 0.9999998866201905

    # Act
    result = await _determine_final_route(
        mock_utterance, mock_top_prediction, mock_probabilities, mock_max_prob
    )

    # Assert
    assert result == "illegal"
    
    # It should build plausible_routes = ['illegal'] (len < 2)
    # It should fall back to top 2: ['illegal', 'qa']
    
    expected_llm_routes = ['illegal', 'qa']
    expected_llm_call = SEMANTIC_ROUTER.format(user_query=mock_utterance, class_list=expected_llm_routes)
    
    mock_get_chat_response.assert_called_once_with(expected_llm_call)


@pytest.mark.asyncio
@patch("src.logic.config", MOCK_CONFIG)
@patch("src.logic.get_chat_response", new_callable=AsyncMock)
async def test_low_confidence_multiple_plausible(
    mock_get_chat_response: AsyncMock, 
):
    """
    Tests the low confidence path (prob < alpha) where multiple routes
    are above the BETA_THRESHOLD.
    - Should call LLM with the plausible routes.
    """
    # Arrange
    mock_get_chat_response.return_value = "sql" # Mocked LLM response
    
    mock_utterance = 'شماره انبارهای سیستم'
    mock_top_prediction = "sql"
    # Both 'sales' and 'products' are > beta (0.5)
    mock_probabilities = [('chitchat', 2.852984267469941e-11), ('illegal', 0.0007070779718326958), ('irrelevant', 2.681493225624694e-12), ('qa', 0.42516598097336894), ('sql', 0.574126941023587)]
    mock_max_prob = 0.574126941023587

    # Act
    result = await _determine_final_route(
        mock_utterance, mock_top_prediction, mock_probabilities, mock_max_prob
    )

    # Assert
    assert result == "sql"
    
    # It should fail the alpha check (0.574126941023587 < 0.90)
    # It should build plausible_routes = ['qa', 'sql'] (len >= 2)
    expected_llm_routes = ['qa', 'sql']
    expected_llm_call = SEMANTIC_ROUTER.format(user_query=mock_utterance, class_list=expected_llm_routes)
    
    mock_get_chat_response.assert_called_once_with(expected_llm_call)

### test _chat_responder

# --- Constants for Mocking ---
MOCK_TEMPLATE_NOT_ANSWER = "I am sorry, I cannot answer that."
MOCK_TEMPLATE_NOT_CONTEXT = "That is outside my knowledge base for {company_name}."


@pytest.fixture
def mock_default_config(mocker: MagicMock) -> MagicMock:
    """Provides a default mock for the 'config' global."""
    default_db_config = {
        "persist_directory": "test_db/",
        "company_name": "TestCo",
        "assistant_name": "Tester",
        "response_type": "default",
        "does_evaluate": False,
        "use_cache": True,
    }
    # Use mocker.patch.dict to mock the config object
    # Updated path
    return mocker.patch.dict("src.logic.config", {
        "database": default_db_config
    }, clear=True)


# --- Test Cases ---

@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_cache_hit_original_utterance(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 1: Cache hit on the *original* user utterance.
    Should return immediately.
    """
    # Arrange
    mock_get_cache.return_value = ("cached_response", "http://example.com")
    history = []
    user_utterance = "hello"

    # Act
    result = await chat_responder_(
        history, user_utterance, use_cache=True, detected_module=""
    )

    # Assert
    expected_result = (user_utterance, "cached_response", "", False, [])
    assert result == expected_result
    mock_get_cache.assert_called_once_with(user_utterance)
    mock_paraphraser.assert_not_called()


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_cache_hit_paraphrased_utterance(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 2: Cache miss on original, but hit on paraphrased utterance.
    """
    # Arrange
    mock_get_cache.side_effect = [
        (None, None), 
        ("cached_paraphrased_response", "http://example.com")
    ]
    mock_paraphraser.return_value = "paraphrased_hello"
    history = [("hi", "there")]
    user_utterance = "hello"

    # Act
    result = await chat_responder_(
        history, user_utterance, use_cache=True, detected_module=""
    )

    # Assert
    expected_result = ("paraphrased_hello", "cached_paraphrased_response", "", False, [])
    assert result == expected_result
    assert mock_get_cache.call_count == 2
    mock_paraphraser.assert_called_once_with(history, user_utterance)


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_needs_clarification(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 3: Cache miss, and prepare_final_context returns do_clarify = True.
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_query"
    mock_prepare_context.return_value = (True, ["module1", "module2"], "some_context")
    
    history = []
    user_utterance = "tell me about stuff"

    # Act
    result = await chat_responder_(
        history, user_utterance, use_cache=False
    )

    # Assert
    expected_result = ("paraphrased_query", "", "", True, ["module1", "module2"])
    assert result == expected_result
    mock_prepare_context.assert_called_once_with(
        "paraphrased_query", 
        database_index="test_db/"
    )
    mock_get_route.assert_not_called()


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_route_sql_with_empty_modules(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 4a: Cache miss, no clarification, route is "sql", modules list is empty.
    Should return ["all"].
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "sql_query"
    mock_prepare_context.return_value = (False, [], "context") # modules is []
    mock_get_route.return_value = "sql"
    
    history = []
    user_utterance = "what is my sales number"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = ("sql_query", "", "", False, ["all"])
    assert result == expected_result
    mock_get_route.assert_called_once_with("sql_query")


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_route_sql_with_existing_module(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 4b: Cache miss, no clarification, route is "sql", modules list has items.
    Should return [modules[0]].
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "sql_query_finance"
    mock_prepare_context.return_value = (False, ["finance", "hr"], "context")
    mock_get_route.return_value = "sql"
    
    history = []
    user_utterance = "what is my finance number"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = ("sql_query_finance", "", "", False, ["finance"])
    assert result == expected_result


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_route_chitchat(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 5: Cache miss, route is "chitchat".
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_hello"
    mock_prepare_context.return_value = (False, [], "chitchat_context")
    mock_get_route.return_value = "chitchat"
    mock_chitchat.return_value = "Hello! I am a test bot."
    
    history = []
    user_utterance = "hello"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = ("paraphrased_hello", "Hello! I am a test bot.", "chitchat_context", False, [])
    assert result == expected_result
    mock_chitchat.assert_called_once_with(
        "paraphrased_hello", 
        history=history, 
        context="chitchat_context"
    )


@pytest.mark.asyncio
@patch("src.logic.template_for_not_answer", MOCK_TEMPLATE_NOT_ANSWER) # Updated path
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_route_illegal(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 6: Cache miss, route is "illegal".
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_bad_word"
    mock_prepare_context.return_value = (False, [], "")
    mock_get_route.return_value = "illegal"
    
    history = []
    user_utterance = "bad word"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = ("paraphrased_bad_word", MOCK_TEMPLATE_NOT_ANSWER, "", False, [])
    assert result == expected_result


@pytest.mark.asyncio
@patch("src.logic.template_for_not_answer", MOCK_TEMPLATE_NOT_ANSWER) # Updated path
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_route_irrelevant(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 7: Cache miss, route is "irrelevant".
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_pizza_query"
    mock_prepare_context.return_value = (False, [], "")
    mock_get_route.return_value = "irrelevant"
    
    history = []
    user_utterance = "how to make pizza"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = ("paraphrased_pizza_query", MOCK_TEMPLATE_NOT_ANSWER, "", False, [])
    assert result == expected_result


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_route_qa_no_context(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 8: Cache miss, route is "qa", but context is empty.
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_query"
    mock_prepare_context.return_value = (False, ["module1"], "") # Context is ""
    mock_get_route.return_value = "qa"
    
    history = []
    user_utterance = "tell me about product x"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = ("paraphrased_query", "", "", False, [])
    assert result == expected_result
    mock_query_responder.assert_not_called()


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_full_qa_path_success(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 9: The full, successful RAG/QA path.
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_query"
    mock_prepare_context.return_value = (False, ["module1"], "This is the RAG context.")
    mock_get_route.return_value = "qa"
    mock_query_responder.return_value = "This is the final LLM answer."
    
    history = []
    user_utterance = "tell me about product x"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = (
        "paraphrased_query", 
        "This is the final LLM answer.", 
        "This is the RAG context.", 
        False, 
        ["module1"]
    )
    assert result == expected_result
    
    mock_query_responder.assert_called_once_with(
        "paraphrased_query",
        "This is the RAG context.",
        history,
        company_name="TestCo",
        assistant_name="Tester",
        answer_type="default"
    )


@pytest.mark.asyncio
@patch("src.logic.template_for_not_answer", MOCK_TEMPLATE_NOT_ANSWER) # Updated path
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_full_qa_path_oos_1(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 10: Full QA path, but response contains 'محدوده دانش من '.
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_query"
    mock_prepare_context.return_value = (False, ["module1"], "This is the RAG context.")
    mock_get_route.return_value = "qa"
    mock_query_responder.return_value = "Sorry, محدوده دانش من is limited."
    
    history = []
    user_utterance = "tell me about product x"

    # Act
    result = await chat_responder_(history, user_utterance, use_cache=False)

    # Assert
    expected_result = (
        "paraphrased_query", 
        MOCK_TEMPLATE_NOT_ANSWER, 
        "This is the RAG context.", 
        False, 
        ["module1"]
    )
    assert result == expected_result


@pytest.mark.asyncio
@patch("src.logic.template_for_not_context", MOCK_TEMPLATE_NOT_CONTEXT) # Updated path
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_full_qa_path_oos_2(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 11: Full QA path, but response contains 'خارج از حوزه کاری'.
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_query"
    mock_prepare_context.return_value = (False, ["module1"], "This is the RAG context.")
    mock_get_route.return_value = "qa"
    mock_query_responder.return_value = "That is خارج از حوزه کاری for me."
    
    history = []
    user_utterance = "tell me about product x"

    # Act
    result = await chat_responder_(
        history, user_utterance, use_cache=False, company_name="TestCo"
    )

    # Assert
    expected_response = MOCK_TEMPLATE_NOT_CONTEXT.format(company_name="TestCo")
    expected_result = (
        "paraphrased_query", 
        expected_response,
        "This is the RAG context.", 
        False, 
        ["module1"]
    )
    assert result == expected_result


@pytest.mark.asyncio
@patch("src.logic.pdb") # Updated path
@patch("src.logic.query_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.chitchat_responder", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_route_for_utterance", new_callable=AsyncMock) # Updated path
@patch("src.logic.prepare_final_context", new_callable=AsyncMock) # Updated path
@patch("src.logic.utterance_paraphraser", new_callable=AsyncMock) # Updated path
@patch("src.logic.get_cache_response", new_callable=AsyncMock) # Updated path
async def test_with_detected_module(
    mock_get_cache: AsyncMock,
    mock_paraphraser: AsyncMock,
    mock_prepare_context: AsyncMock,
    mock_get_route: AsyncMock,
    mock_chitchat: AsyncMock,
    mock_query_responder: AsyncMock,
    mock_pdb: MagicMock,
    mock_default_config: MagicMock
):
    """
    Tests Path 12: A module is passed in from the start.
    Ensures 'prepare_final_context' is called correctly.
    """
    # Arrange
    mock_get_cache.return_value = (None, None)
    mock_paraphraser.return_value = "paraphrased_query"
    mock_prepare_context.return_value = (False, ["finance"], "Finance context.")
    mock_get_route.return_value = "qa"
    mock_query_responder.return_value = "Your finance answer."
    
    history = []
    user_utterance = "what's my budget"
    detected_module = "finance" # This is the key input

    # Act
    result = await chat_responder_(
        history, user_utterance, use_cache=False, detected_module=detected_module
    )

    # Assert
    # Check that prepare_final_context was called with the input_module
    mock_prepare_context.assert_called_once_with(
        "paraphrased_query",
        database_index="test_db/",
        input_module="finance"
    )
    
    expected_result = (
        "paraphrased_query", 
        "Your finance answer.", 
        "Finance context.", 
        False, 
        ["finance"]
    )
    assert result == expected_result