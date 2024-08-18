HTML_STYLE_FOR_RTL_INPUT_ELEMENT = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    .rtl-text {
        font-family: 'Vazirmatn', sans-serif;
        direction: rtl;
        text-align: right;
    }
    </style>
"""
HTML_RTL_INPUT_TITLE = """
        <div class="rtl-text">
            <h1>{}</h1>
        </div>
        """

HTML_RTL_INPUT_BODY = """
        <div class="rtl-text">
            <p>{}</p>
        </div>
        """
