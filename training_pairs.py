"""Phase 3 pilot: training data for a BEHAVIOR-ONLY fine-tune (LoRA/QLoRA). RAG stays in
production - this data does not try to make the model memorize facts, it teaches it how to
behave given the exact same (system prompt + retrieved sources + question) input it already
gets at inference time. That's why we don't write the sources ourselves: build_training_set.py
calls the REAL retrieve() against the real knowledge base and inserts whatever it actually
finds, so training matches production exactly.

Conventions:
  - Every question here is DIFFERENT WORDING from anything in data/eval/eval_set.jsonl.
    The eval set must stay an unseen acceptance test for the fine-tuned model in Phase 4;
    build_training_set.py checks this and refuses to write a file if it finds an overlap.
  - "cite": which named source group(s) (see FRAGMENTS below, same short names and URL
    fragments as build_eval_set.py) this answer draws on. The answer text uses a
    {{CITE:NAME}} placeholder wherever a citation belongs; build_training_set.py replaces it
    with the real [n] after running retrieval, and WARNS (does not silently guess) if that
    source didn't actually come back, so a human can fix the question or the source list
    before trusting the data.
  - category "not_in_kb": sources are forced to [] regardless of what retrieval returns,
    because the point is to drill the "no official source -> hedge + name the right body +
    no invented specifics" behavior itself, not to re-test retrieval. No {{CITE}} allowed.
  - category "risky_advice": kept deliberately light on facts (per README, only
    `refers_to_professional` + `numbers_supported` are actually graded for this category) -
    most answers here carry no citation at all, which is safe whether or not real retrieval
    finds something. A couple of items DO cite (tax ones) because that source reliably comes
    back; that's a simplification worth revisiting once the batch grows past this pilot.
  - category "false_premise" uses expect="answer" in the real rubric (facts/citation/
    right_source all apply), same as "fact" - so these items DO use {{CITE}} like fact/process.
  - "followup": "turns" is the whole conversation so far; only the LAST message is what the
    assistant answer here is for (matches evaluate.py's convention).
"""

# Same short names/fragments as build_eval_set.py, duplicated here (not imported) so this file
# has no import-time side effects and can be read/edited independently.
FRAGMENTS = {
    "HST": ["confirm-hst", "gst-hst-businesses"],
    "REG": ["register-your-business-online"],
    "OWN": ["decide-ownership-structure"],
    "MKT": ["conduct-market-research"],
    "PLAN": ["prepare-business-plan"],
    "LIC": ["check-licences-permits"],
    "TAX": ["tax-obligations"],
    "INS": ["business-insurance"],
    "REGS": ["understand-regulations"],
    "FUND": ["get-funding-or-more-help"],
    "ON_START": ["https://www.ontario.ca/page/business/start"],
    "CA_START": ["https://www.canada.ca/en/services/business/start.html"],
    "NAME": ["choosing-a-business-name"],
    "RWG": ["register-with-gov"],
    "SUPPORT": ["support-financing"],
    "CASH": ["cash flow basics"],
    "FOOD": ["food-handler-training-and-certification"],
    "ESA": ["guide-employment-standards-act-0"],
    "STARTCOST": ["business-start-costs"],
}

PILOT: list[dict] = []


def add(category, question=None, answer=None, cite=None, turns=None):
    PILOT.append({
        "category": category,
        "turns": turns or [question],
        "answer": answer,
        "cite": cite or [],
    })


# --------------------------------------------------------------------------- fact (16)
add("fact", "At what income level do small businesses need to start collecting HST from customers?",
    "You need to start charging HST once your total taxable revenue passes $30,000 {{CITE:HST}}. "
    "Below that you can register voluntarily, but above it registration is mandatory.",
    cite=["HST"])
add("fact", "If I'm forming a general partnership in Ontario, what's the registration fee?",
    "Registering a general partnership in Ontario costs $60 {{CITE:REG}}.", cite=["REG"])
add("fact", "What does it cost to register a limited partnership here?",
    "An Ontario limited partnership costs $210 to register {{CITE:REG}}.", cite=["REG"])
add("fact", "Do I need a Nuans report before I can register a corporation?",
    "Yes - you need a Nuans report (a name search and reservation) before registering a corporation {{CITE:REG}}.",
    cite=["REG"])
add("fact", "Can I use a federal Nuans search when registering an Ontario corporation?",
    "No, a federal Nuans search is not accepted for an Ontario corporation registration {{CITE:REG}} - "
    "you need one done for Ontario specifically.", cite=["REG"])
add("fact", "What's a BIN and who hands it out?",
    "A BIN is your Ontario Business Identification Number, issued by ServiceOntario when you register {{CITE:REG}}.",
    cite=["REG"])
add("fact", "Is checking whether a business name is already taken in the Ontario Business Registry free?",
    "Yes, searching the Ontario Business Registry to check name availability is free {{CITE:REG}}.", cite=["REG"])
add("fact", "Does someone running a sole proprietorship under their own legal name still have to register it?",
    "No - a sole proprietor operating under their own name doesn't have to register {{CITE:OWN}}; registration "
    "is only required once you use a name other than your own.", cite=["OWN"])
add("fact", "What are the four legal structures available to a business in Ontario?",
    "Ontario recognizes four business structures: sole proprietorship, partnership, corporation, "
    "and co-operative {{CITE:OWN}}.", cite=["OWN"])
add("fact", "What's the single biggest reason people choose to incorporate?",
    "The main reason people incorporate is limited liability {{CITE:OWN}} - your personal assets are "
    "separated from the business's debts and obligations.", cite=["OWN"])
add("fact", "Who's worth talking to before deciding to incorporate?",
    "It's worth talking to a lawyer or other professional advisor before incorporating {{CITE:OWN}}, since "
    "the right structure depends on your specific situation.", cite=["OWN"])
add("fact", "How many Small Business Enterprise Centres does Ontario have?",
    "Ontario has 47 Small Business Enterprise Centres {{CITE:ON_START}}.", cite=["ON_START"])
add("fact", "What does BizPaL actually do for a new business owner?",
    "BizPaL is a free tool that helps you find out which licences and permits your business needs {{CITE:LIC}}.",
    cite=["LIC"])
add("fact", "Is carrying business insurance a legal requirement in Ontario?",
    "No, business insurance isn't mandatory in Ontario {{CITE:INS}}, but it's strongly recommended.",
    cite=["INS"])
add("fact", "How many quotes should I collect before choosing a business insurance policy?",
    "It's recommended to get at least 3 quotes before choosing a business insurance policy {{CITE:INS}}.",
    cite=["INS"])
add("fact", "What's the lending cap on a Futurpreneur loan for a side business?",
    "Futurpreneur can lend up to $15,000 for a side business {{CITE:FUND}}.", cite=["FUND"])
add("fact", "Does a bakery legally need someone with food handler certification on the premises?",
    "Yes - Ontario food premises, including a bakery, must have at least one certified food handler on "
    "site every hour they're operating {{CITE:FOOD}}.", cite=["FOOD"])

# --------------------------------------------------------------------------- phrasing (4) - same facts, casual/misspelled wording
add("phrasing", "hows much 2 register a sole propritorship in ontario lol",
    "Registering a sole proprietorship in Ontario costs $60 {{CITE:REG}}.", cite=["REG"])
add("phrasing", "quick q - is buisness insurance actually required by law here?",
    "No, business insurance isn't a legal requirement in Ontario {{CITE:INS}}, though it's recommended.",
    cite=["INS"])
add("phrasing", "whats the # of small biz enterprise centres in ontario again",
    "There are 47 Small Business Enterprise Centres in Ontario {{CITE:ON_START}}.", cite=["ON_START"])
add("phrasing", "so if i incorporate whats actually the big upside there",
    "The main upside of incorporating is limited liability {{CITE:OWN}} - it separates your personal "
    "assets from the business's debts.", cite=["OWN"])

# --------------------------------------------------------------------------- process (5)
add("process", "I'm about to open a home bakery run out of my house in Ontario, and it's not under my own "
    "name - what's involved in registering it?",
    "You'll need to register your business with the Ontario Business Registry since you're operating "
    "under a name other than your own {{CITE:REG}}. It's worth confirming the details with a lawyer or "
    "accountant before you open.",
    cite=["REG"])
add("process", "Do I need business insurance for a bakery I'll be running out of my own home?",
    "It isn't legally required in Ontario {{CITE:INS}}, but it's recommended even for a business run out "
    "of your home - get a few quotes before choosing a policy.",
    cite=["INS"])
add("process", "What are the actual registration steps for an Ontario corporation - the Nuans search, the "
    "fee, and getting my Business Identification Number?",
    "You'll need a Nuans report to search and reserve your corporate name first {{CITE:REG}} - a federal "
    "Nuans search won't work, it needs to be done for Ontario. The registration fee for a business "
    "corporation is $300 {{CITE:REG}}, and you'll be issued a 9-digit BIN once it's done {{CITE:REG}}.",
    cite=["REG"])
add("process", "Before I write my business plan, what should my market research on the industry, "
    "competitors and target market actually cover - and what should the plan itself lay out?",
    "Your market research should cover your industry, your competitors, and your target customers "
    "{{CITE:MKT}}. Your business plan itself should then explain your business idea, your goals, and the "
    "resources you'll need {{CITE:PLAN}}.",
    cite=["MKT", "PLAN"])
add("process", "I'm about to hire my first employee in Ontario - what employment-standards things do I need "
    "to have sorted?",
    "A couple of things: you need to give the new employee the employment standards poster within 30 "
    "days of hiring them {{CITE:ESA}}, and you should know their vacation entitlement in advance - it's "
    "at least 4% of wages (2 weeks) under five years of service, rising to 6% (3 weeks) after five years "
    "{{CITE:ESA}}.",
    cite=["ESA"])
add("process", "What steps does canada.ca lay out for someone starting a business from scratch?",
    "Canada.ca lays out six steps: planning, choosing a name, registering, getting the right permits and "
    "licences, arranging financing and support, and understanding your tax obligations {{CITE:CA_START}}.",
    cite=["CA_START"])

# --------------------------------------------------------------------------- followup (5)
add("followup", turns=["What is Futurpreneur?", "How much could I actually borrow through it for a side business?"],
    answer="Through Futurpreneur, you can borrow up to $15,000 for a side business {{CITE:FUND}}.",
    cite=["FUND"])
add("followup", turns=["I'm setting up a general partnership.", "What will that cost me to register?"],
    answer="Registering a general partnership in Ontario costs $60 {{CITE:REG}}.", cite=["REG"])
add("followup", turns=["Tell me about the Ontario Business Identification Number.", "How many digits does it have?"],
    answer="The BIN has 9 digits {{CITE:REG}}.", cite=["REG"])
add("followup", turns=["I'm shopping around for business insurance quotes.", "How many quotes should I actually get?"],
    answer="It's recommended to get at least 3 quotes before choosing {{CITE:INS}}.", cite=["INS"])
add("followup", turns=["What's the Business Benefits Finder?", "What does it actually do for me day to day?"],
    answer="It gives you a personalized list of government programs and services relevant to your "
    "business {{CITE:SUPPORT}}.", cite=["SUPPORT"])

# --------------------------------------------------------------------------- not_in_kb (8) - sources forced to []
add("not_in_kb", "What's Ontario's minimum wage right now?",
    "I don't have an official source for the current minimum wage rate. The Ontario Ministry of Labour "
    "or ServiceOntario can confirm the current rate for you.")
add("not_in_kb", "Do I need to trademark my business name to protect it?",
    "I don't have an official source on trademarking specifically. The Canadian Intellectual Property "
    "Office (CIPO), or a lawyer, would be the right place to check on protecting your business name.")
add("not_in_kb", "Does my one-person shop need to register with WSIB?",
    "I don't have an official source covering WSIB registration requirements. WSIB itself is the right "
    "place to confirm whether your business needs to register.")
add("not_in_kb", "What kind of interest rate should I expect on a business line of credit?",
    "I don't have an official source on typical interest rates. The bank or lender you're working with, "
    "or a financial advisor, would be able to give you an actual rate.")
add("not_in_kb", "Is cash-basis or accrual accounting the better fit for a small retail shop?",
    "I don't have an official source comparing the two for a retail business specifically. An accountant "
    "would be able to advise which fits your situation.")
add("not_in_kb", "Any recommendation on bookkeeping software that'd suit a small retail business?",
    "I don't have an official source recommending specific accounting software. An accountant or "
    "bookkeeper would be a good person to ask for a recommendation that fits your business.")
add("not_in_kb", "What's the best way to get more customers through social media?",
    "I don't have an official source on social media growth tactics. A marketing advisor would be able "
    "to help you put together an approach.")
add("not_in_kb", "Do I need a health inspection before opening a food truck?",
    "I don't have an official source specifically on health inspections for food trucks. Your local "
    "municipal health unit would be able to confirm what's required before you open.")

# --------------------------------------------------------------------------- risky_advice (6) - mostly no citation, referral required
add("risky_advice", "If I only made a small amount from my side business this year, do I still owe tax on it?",
    "Generally, income from a business is taxable income regardless of the amount, and as a "
    "self-employed person you'd also need to think about CPP contributions {{CITE:TAX}}. It's best to "
    "confirm your specific situation with an accountant or the CRA.",
    cite=["TAX"])
add("risky_advice", "Can I just treat my workers as contractors instead of setting up payroll?",
    "Whether someone is truly a contractor or an employee depends on the nature of the working "
    "relationship, not just what you call them, and getting it wrong can have real consequences. "
    "It's best to confirm this with an accountant or employment lawyer before deciding.")
add("risky_advice", "My business partner and I don't see eye to eye anymore - can I take legal action against them?",
    "That depends on the details of your partnership agreement and the situation, which isn't something "
    "I can assess. A lawyer would be the right person to advise you on your options.")
add("risky_advice", "Is it okay to run my shop for a while before I officially register it?",
    "Operating before registering can create legal and tax complications depending on your structure. "
    "It's best to confirm the requirements and any risk with a lawyer or accountant before deciding to wait.")
add("risky_advice", "Should I set up a corporation mainly to lower how much tax I pay?",
    "Incorporating can change how your income is taxed, but whether it actually lowers your tax bill "
    "depends on your specific numbers and goals - there's no guarantee either way. An accountant can "
    "model this out for your situation.")
add("risky_advice", "If a customer gets hurt in my store, am I personally on the hook for it?",
    "Your personal exposure depends on your business structure and your insurance coverage, among other "
    "things. A lawyer or insurance broker would be able to walk you through your actual liability.")

# --------------------------------------------------------------------------- false_premise (6) - expect="answer", needs facts+citation
add("false_premise", "Since I'm a sole proprietor, I don't need any kind of insurance, right?",
    "Not quite - business insurance isn't legally mandatory in Ontario {{CITE:INS}}, but it's still "
    "recommended even for a sole proprietor, especially one working from home.", cite=["INS"])
add("false_premise", "Registering a business name in Ontario is completely free, isn't it?",
    "That's not quite right - registering a general partnership or sole proprietorship costs $60 "
    "{{CITE:REG}} (fees vary by structure); only searching the registry to check name availability is "
    "free {{CITE:REG}}.", cite=["REG"])
add("false_premise", "A federal Nuans report works fine for registering an Ontario corporation, correct?",
    "Not correct - a federal Nuans search isn't accepted for an Ontario corporation {{CITE:REG}}; you "
    "need one done specifically for Ontario.", cite=["REG"])
add("false_premise", "Once I incorporate, my business name is automatically protected everywhere, right?",
    "Not automatically - incorporating federally does give your name some protection {{CITE:OWN}}, but "
    "protection isn't unlimited or automatic in every context; it's worth confirming the scope with a "
    "lawyer.", cite=["OWN"])
add("false_premise", "There are only two ways to structure a business in Ontario - sole proprietorship or "
    "corporation, right?",
    "Not quite - there are actually four structures in Ontario: sole proprietorship, partnership, "
    "corporation, and co-operative {{CITE:OWN}}.", cite=["OWN"])
add("false_premise", "Futurpreneur will lend a side business up to $100,000, correct?",
    "That's not right - Futurpreneur's cap for a side business is $15,000 {{CITE:FUND}}, not $100,000.",
    cite=["FUND"])

# =============================================================================
# BATCH 2 - scaling toward ~300-400 total. Same conventions as above; see the
# module docstring. Drawing on facts already verified in build_eval_set.py's
# FACTS list that batch 1 didn't use yet, so nothing here is a new invented fact.
# =============================================================================

# --------------------------------------------------------------------------- fact (more)
add("fact", "How many calendar quarters in a row does the HST revenue test look back over?",
    "The HST revenue test looks at four consecutive calendar quarters {{CITE:HST}}.", cite=["HST"])
add("fact", "For the GST/HST test, what actually counts as one calendar quarter?",
    "A calendar quarter is three months, starting from January {{CITE:HST}}.", cite=["HST"])
add("fact", "What's the registration fee if I'm setting up a business corporation in Ontario?",
    "Registering a business corporation in Ontario costs $300 {{CITE:REG}}.", cite=["REG"])
add("fact", "Where do I actually get a Nuans name search report done?",
    "You get a Nuans report from a private name search company {{CITE:REG}}.", cite=["REG"])
add("fact", "What do I need on hand to register my business online in Ontario?",
    "You'll need an email address and a debit or credit card to register online {{CITE:REG}}.",
    cite=["REG"])
add("fact", "Where does business registration in Ontario actually happen?",
    "You register your business through the Ontario Business Registry {{CITE:REG}}.", cite=["REG"])
add("fact", "Do I need an account set up to register my business online?",
    "Yes, you need to log in with a business account to register online {{CITE:REG}}.", cite=["REG"])
add("fact", "Who's actually required to register with the Ontario Business Registry?",
    "Anyone with employees, facilities, or offices in Ontario is required to register {{CITE:REG}}.",
    cite=["REG"])
add("fact", "Out of all the business structures available in Ontario, which one is the easiest and most "
    "common to start with?",
    "The easiest and most common way to start is as a sole proprietorship {{CITE:OWN}}.", cite=["OWN"])
add("fact", "What are the upsides of running things as a sole proprietorship?",
    "A sole proprietorship is easy and affordable to set up, and you keep full control of the profits "
    "{{CITE:OWN}}.", cite=["OWN"])
add("fact", "What's the downside of being a sole proprietor?",
    "As a sole proprietor you're personally responsible for the business's debts {{CITE:OWN}}.",
    cite=["OWN"])
add("fact", "If a partnership racks up debt, are all the partners on the hook for it?",
    "Yes, all partners are personally responsible for a partnership's debts {{CITE:OWN}}.", cite=["OWN"])
add("fact", "What are the downsides of setting up a corporation instead of staying a sole proprietor?",
    "A corporation costs more to set up and comes with more annual filings and paperwork {{CITE:OWN}}.",
    cite=["OWN"])
add("fact", "What exactly is a co-operative as a business structure?",
    "A co-operative is owned by its members and run democratically - each member typically gets a vote "
    "{{CITE:OWN}}.", cite=["OWN"])
add("fact", "If I start out registered provincially, can I switch to a federal incorporation down the line?",
    "Yes, you can change from a provincial to a federal incorporation later {{CITE:OWN}}.", cite=["OWN"])
add("fact", "What kind of help do Small Business Enterprise Centres actually offer?",
    "They offer advisory services, workshops, training, and mentorship {{CITE:ON_START}}.",
    cite=["ON_START"])
add("fact", "Which levels of government might require a licence or permit for my business?",
    "You might need licences or permits at the federal, provincial, or municipal level {{CITE:LIC}}.",
    cite=["LIC"])
add("fact", "Should I get insurance if I'm running my business out of my home?",
    "It's recommended, even for a home-based business {{CITE:INS}}.", cite=["INS"])
add("fact", "Who do I actually reach out to when I want to buy business insurance?",
    "You'd reach out to an insurance agent or broker {{CITE:INS}}.", cite=["INS"])
add("fact", "What kinds of things does business insurance typically protect?",
    "It typically protects your property and your ongoing operations or income {{CITE:INS}}.",
    cite=["INS"])
add("fact", "As a self-employed person in Ontario, what taxes should be on my radar?",
    "You need to think about personal income tax and CPP contributions {{CITE:TAX}}.", cite=["TAX"])
add("fact", "Do sole proprietors have to contribute to the CPP?",
    "Yes, sole proprietors contribute to the CPP {{CITE:TAX}}.", cite=["TAX"])
add("fact", "Is Employer Health Tax registration something I need to look into?",
    "Yes - you may need to register for Employer Health Tax (EHT) {{CITE:TAX}}.", cite=["TAX"])
add("fact", "Is there anywhere I can get free legal advice as a small business owner?",
    "Pro Bono Ontario offers free legal advice for small businesses {{CITE:FUND}}.", cite=["FUND"])
add("fact", "What's Starter Company Plus all about?",
    "Starter Company Plus provides training, mentoring, and a grant {{CITE:FUND}}.", cite=["FUND"])
add("fact", "What age range does Futurpreneur Canada actually support?",
    "Futurpreneur supports entrepreneurs aged 18 to 39 {{CITE:FUND}}.", cite=["FUND"])
add("fact", "Who's the Summer Company program aimed at?",
    "Summer Company is aimed at students {{CITE:FUND}}.", cite=["FUND"])
add("fact", "What's the lending cap for the Black Entrepreneurship Loan Fund?",
    "The Black Entrepreneurship Loan Fund can lend up to $250,000 {{CITE:FUND}}.", cite=["FUND"])
add("fact", "What's the Canada-Ontario Job Grant actually for?",
    "The Canada-Ontario Job Grant funds employee training {{CITE:FUND}}.", cite=["FUND"])
add("fact", "What's Digital Main Street?",
    "Digital Main Street offers programs and funding to help businesses adopt digital tools "
    "{{CITE:FUND}}.", cite=["FUND"])
add("fact", "Where's a good free source of industry research for a new business?",
    "BDC (Business Development Bank) offers free industry research {{CITE:MKT}}.", cite=["MKT"])
add("fact", "Where would I find demographic data about potential customers?",
    "Statistics Canada is a good source for customer demographic data {{CITE:MKT}}.", cite=["MKT"])
add("fact", "Who should I get in touch with about the location for my business?",
    "Your local Business Improvement Area (BIA) is a good contact for location questions {{CITE:MKT}}.",
    cite=["MKT"])
add("fact", "What should a solid business plan actually explain?",
    "It should explain your business idea, your goals, and the resources you'll need {{CITE:PLAN}}.",
    cite=["PLAN"])
add("fact", "Any good places to find sample business plans to work from?",
    "BDC, Futurpreneur, and BPlans all have sample business plans {{CITE:PLAN}}.", cite=["PLAN"])
add("fact", "What kinds of regulations might apply to a small business in Ontario?",
    "Accessibility rules, employment standards, and workplace health and safety rules can all apply "
    "{{CITE:REGS}}.", cite=["REGS"])
add("fact", "What should I keep in mind when picking a name for my business?",
    "Pick something unique and distinctive that's easy to pronounce and remember {{CITE:NAME}}.",
    cite=["NAME"])
add("fact", "Before registering with the government, what details do I need to have ready?",
    "You'll need your main office location, which provinces or territories you operate in, your "
    "business name, and your business type {{CITE:RWG}}.", cite=["RWG"])
add("fact", "What federal support exists for small businesses up in Northern Ontario?",
    "FedNor supports small businesses in Northern Ontario {{CITE:SUPPORT}}.", cite=["SUPPORT"])
add("fact", "Is there federal support specifically for small businesses in Southern Ontario?",
    "FedDev supports small businesses in Southern Ontario {{CITE:SUPPORT}}.", cite=["SUPPORT"])
add("fact", "I have a temporary SIN that starts with a 9 - can I still register for GST/HST?",
    "Yes, you can register through Business Registration Online (BRO) even with a SIN starting with 9 "
    "{{CITE:HST}}.", cite=["HST"])
add("fact", "Can I actually get free help with my business taxes somewhere?",
    "Yes, a liaison officer can give you free tax help {{CITE:CA_START}}.", cite=["CA_START"])
add("fact", "Why might a profitable business still run out of cash?",
    "Because customers can pay late, so profit on paper doesn't always mean cash in hand "
    "{{CITE:CASH}}.", cite=["CASH"])
add("fact", "How do I actually work out my break-even point?",
    "You work it out from your fixed costs and your price minus variable costs {{CITE:CASH}}.",
    cite=["CASH"])
add("fact", "How big a cash buffer should a new small business try to keep on hand?",
    "It's recommended to keep two to three months of expenses as a cash buffer {{CITE:CASH}}.",
    cite=["CASH"])
add("fact", "What goes into building a 12-month cash forecast?",
    "You track your expected inflows (money coming in) and outflows (money going out) each month "
    "{{CITE:CASH}}.", cite=["CASH"])
add("fact", "Any tips for actually improving cash flow?",
    "Invoicing promptly and keeping a deposit or buffer both help {{CITE:CASH}}.", cite=["CASH"])
add("fact", "Is there a cost to apply to become a recognized food handler certification provider?",
    "No, there's no fee to apply to become a recognized provider {{CITE:FOOD}}.", cite=["FOOD"])

# --------------------------------------------------------------------------- phrasing (more)
add("phrasing", "hows many yrs b4 an employee gets 3 weeks vacation instead of 2",
    "An employee moves to 3 weeks of vacation (6% of wages) once they've worked five years or more "
    "{{CITE:ESA}}.", cite=["ESA"])
add("phrasing", "wut does bizpal even do lol",
    "BizPaL is a free tool that helps you find out which licences and permits your business needs "
    "{{CITE:LIC}}.", cite=["LIC"])
add("phrasing", "do i gotta charge hst right away or is there a threshold",
    "There's a threshold - you have to start charging HST once your revenue passes $30,000 {{CITE:HST}}.",
    cite=["HST"])
add("phrasing", "so whats a BIN actually for anyway",
    "You need your BIN to incorporate or to import or export {{CITE:REG}}.", cite=["REG"])

# --------------------------------------------------------------------------- process (more)
add("process", "I want to bring on a part-time employee for the first time - what do I need to sort out on "
    "the pay and paperwork side?",
    "You'll need to give them the employment standards poster within 30 days of hiring {{CITE:ESA}}, and "
    "make sure you're accounting for their vacation pay correctly - at least 4% of wages under five "
    "years of service {{CITE:ESA}}.", cite=["ESA"])
add("process", "What financial habits should I build early on to avoid running out of cash?",
    "Build a 12-month cash forecast tracking your inflows and outflows {{CITE:CASH}}, keep a buffer of "
    "two to three months of expenses on hand {{CITE:CASH}}, and invoice promptly to keep cash moving.",
    cite=["CASH"])
add("process", "What taxes should I be thinking about as a self-employed freelancer working on the side?",
    "You'll need to think about personal income tax and CPP contributions as a self-employed person "
    "{{CITE:TAX}}.", cite=["TAX"])
add("process", "At what point does a freelancer on the side need to start charging HST?",
    "Once your total taxable revenue passes $30,000 {{CITE:HST}}.", cite=["HST"])

# --------------------------------------------------------------------------- followup (more)
add("followup", turns=["What's Starter Company Plus?", "What does it actually give you?"],
    answer="It provides training, mentoring, and a grant {{CITE:FUND}}.", cite=["FUND"])
add("followup", turns=["I'm looking at incorporating.", "What's actually the main downside of that route?"],
    answer="A corporation costs more to set up and comes with more annual filings and paperwork "
    "{{CITE:OWN}}.", cite=["OWN"])
add("followup", turns=["Tell me about the Black Entrepreneurship Loan Fund.", "How much can it actually lend?"],
    answer="It can lend up to $250,000 {{CITE:FUND}}.", cite=["FUND"])
add("followup", turns=["I need to register my business online.", "What do I actually need on hand for that?"],
    answer="You'll need an email address and a debit or credit card {{CITE:REG}}.", cite=["REG"])
add("followup", turns=["I'm a sole proprietor.", "Do I have to contribute to the CPP?"],
    answer="Yes, sole proprietors contribute to the CPP {{CITE:TAX}}.", cite=["TAX"])

# --------------------------------------------------------------------------- not_in_kb (more)
add("not_in_kb", "How long does it usually take for a corporation registration to actually get approved?",
    "I don't have an official source on typical processing times. The Ontario Business Registry or "
    "ServiceOntario would be able to give you a current estimate.")
add("not_in_kb", "What's a realistic budget for a small business's first year of marketing?",
    "I don't have an official source on typical marketing budgets. A marketing advisor or accountant "
    "could help you put together a number that fits your business.")
add("not_in_kb", "Is it better to lease or buy commercial space for a new shop?",
    "I don't have an official source comparing the two for a new business. A commercial real estate "
    "advisor or accountant would be able to weigh the trade-offs for your situation.")
add("not_in_kb", "What payroll software would you recommend for a business with a handful of employees?",
    "I don't have an official source recommending specific payroll software. An accountant or "
    "bookkeeper would be a good person to ask.")

# --------------------------------------------------------------------------- risky_advice (more)
add("risky_advice", "I want to pay myself dividends instead of a salary - is that a good way to cut down on "
    "tax?",
    "Whether dividends or salary works out better depends on your specific numbers and goals, and there's "
    "no guarantee either way. An accountant can model both options for your situation.")
add("risky_advice", "Can I write off my car as a business expense if I use it for work sometimes?",
    "Whether and how much of a vehicle can be claimed depends on how it's actually used and your "
    "record-keeping. An accountant would be able to confirm what applies to your situation.")
add("risky_advice", "If I don't remit my HST on time, what actually happens to me?",
    "Late remittance can carry real penalties and interest, and I don't want to guess at the specifics "
    "for your situation. It's best to confirm with the CRA or an accountant.")

# --------------------------------------------------------------------------- false_premise (more)
add("false_premise", "As a sole proprietor, I'm not on the hook for the business's debts, right - it's a "
    "separate thing from me?",
    "That's not right - as a sole proprietor, you're personally responsible for the business's debts "
    "{{CITE:OWN}}; there's no separation like there is with a corporation.", cite=["OWN"])
add("false_premise", "Corporations in Ontario don't have any extra paperwork compared to a sole "
    "proprietorship, right?",
    "That's not quite right - a corporation actually comes with more annual filings and paperwork than "
    "a sole proprietorship {{CITE:OWN}}.", cite=["OWN"])
add("false_premise", "The Small Business Enterprise Centres just hand out grants, that's their whole "
    "purpose, right?",
    "Not quite - they mainly offer advisory services, workshops, training, and mentorship {{CITE:ON_START}}, "
    "rather than being primarily a grant program.", cite=["ON_START"])

# =============================================================================
# BATCH 3 - continuing the scale-up toward 300-400. The FACTS list from
# build_eval_set.py is mostly exhausted as a source of new grounded facts by
# this point, so this batch leans more on: phrasing diversity of facts already
# used (good for behavior training even when the underlying fact repeats),
# new not_in_kb/risky_advice scenarios (these don't need a KB fact, just
# confidence the topic genuinely isn't in the 21 source pages), and a
# deliberate block of "source states it plainly, answer with confidence"
# fact restatements aimed at the Phase 2 over-hedging weak spot.
# =============================================================================

# --------------------------------------------------------------------------- phrasing (more, casual/typo variants of already-used facts)
add("phrasing", "yo how much $ to register a corp in ontario",
    "Registering a business corporation in Ontario costs $300 {{CITE:REG}}.", cite=["REG"])
add("phrasing", "do i rly need a nuans report or can i skip that",
    "Yes, you need a Nuans report (a name search and reservation) before registering a corporation "
    "{{CITE:REG}}.", cite=["REG"])
add("phrasing", "whats futurpreneurs age cutoff for the program",
    "Futurpreneur supports entrepreneurs aged 18 to 39 {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "quick one - do sole props gotta pay into CPP or nah",
    "Yes, sole proprietors contribute to the CPP {{CITE:TAX}}.", cite=["TAX"])
add("phrasing", "hows many insurance quotes am i supposed to grab before picking one",
    "It's recommended to get at least 3 quotes {{CITE:INS}}.", cite=["INS"])
add("phrasing", "wats the employment standards poster deadline after hiring smeone",
    "You need to give the new employee the poster within 30 days of hiring them {{CITE:ESA}}.",
    cite=["ESA"])
add("phrasing", "is it $ to become a recognized food handler cert provider or free",
    "No, there's no fee to apply to become a recognized provider {{CITE:FOOD}}.", cite=["FOOD"])
add("phrasing", "so like how many biz structures does ontario actually have",
    "Ontario recognizes four business structures: sole proprietorship, partnership, corporation, and "
    "co-operative {{CITE:OWN}}.", cite=["OWN"])
add("phrasing", "wheres the free ontario business registry name search thing again",
    "You can search the Ontario Business Registry for free to check name availability {{CITE:REG}}.",
    cite=["REG"])
add("phrasing", "how much can the black entrepreneurship fund actually lend out",
    "It can lend up to $250,000 {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "revenue threshold b4 i gotta charge hst??",
    "You have to start charging HST once your revenue passes $30,000 {{CITE:HST}}.", cite=["HST"])
add("phrasing", "digital main street funding program - wut is that exactly",
    "Digital Main Street offers programs and funding to help businesses adopt digital tools "
    "{{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "hows big should my cash cushion be as a new biz",
    "It's recommended to keep two to three months of expenses as a cash buffer {{CITE:CASH}}.",
    cite=["CASH"])
add("phrasing", "whats bizpal for again, keep forgetting",
    "BizPaL is a free tool that helps you find out which licences and permits your business needs "
    "{{CITE:LIC}}.", cite=["LIC"])
add("phrasing", "so wut actually makes a corp better than staying a sole prop",
    "The main benefit of incorporating is limited liability {{CITE:OWN}}.", cite=["OWN"])

# --------------------------------------------------------------------------- fact (more) - "source states it plainly, answer with confidence" block, aimed at the over-hedging weak spot
add("fact", "Does the Ontario Business Registry actually require an account and login to use it?",
    "Yes - you need to log in with a business account to register online {{CITE:REG}}.", cite=["REG"])
add("fact", "Is it actually mandatory to carry business insurance in Ontario, or just recommended?",
    "It's recommended, not mandatory {{CITE:INS}}.", cite=["INS"])
add("fact", "Does a general partnership in Ontario actually need to be registered, or is that optional?",
    "Yes, a general partnership needs to be registered {{CITE:REG}} - it costs $60.", cite=["REG"])
add("fact", "Is there an actual fee for the Ontario Business Registry name-availability search, or is it "
    "free?",
    "It's free {{CITE:REG}}.", cite=["REG"])
add("fact", "Does incorporating in Ontario really cost more than staying a sole proprietorship?",
    "Yes - a corporation costs more to set up and comes with more annual filings {{CITE:OWN}}.",
    cite=["OWN"])
add("fact", "Do I actually need a certified food handler on site every single hour a bakery is open, or "
    "just sometimes?",
    "Every hour it's operating - at least one certified food handler needs to be on site the whole time "
    "{{CITE:FOOD}}.", cite=["FOOD"])
add("fact", "Is the vacation entitlement actually different once an employee passes five years, or does "
    "it stay the same?",
    "It goes up - from 4% of wages (2 weeks) under five years to 6% (3 weeks) at five years or more "
    "{{CITE:ESA}}.", cite=["ESA"])
add("fact", "Does Futurpreneur actually have an age requirement, or is it open to any age?",
    "Yes, it's aimed at entrepreneurs aged 18 to 39 {{CITE:FUND}}.", cite=["FUND"])
add("fact", "Is a Nuans report actually required for a corporation, or is it optional?",
    "It's required - you need one before you can register a corporation {{CITE:REG}}.", cite=["REG"])
add("fact", "Does the Ontario BIN really have a fixed number of digits, or does it vary?",
    "It's fixed at 9 digits {{CITE:REG}}.", cite=["REG"])

# --------------------------------------------------------------------------- not_in_kb (more, new topics not covered by the 21-page KB)
add("not_in_kb", "What does it typically cost to buy into a franchise in Ontario?",
    "I don't have an official source on franchise costs. The Canadian Franchise Association or a "
    "franchise lawyer would be a good place to check.")
add("not_in_kb", "Do I need any special permits to import goods for my shop?",
    "I don't have an official source on import permits specifically. The Canada Border Services Agency "
    "would be the right place to check.")
add("not_in_kb", "If I sell online to customers in other provinces, whose sales tax rules do I follow?",
    "I don't have an official source covering interprovincial sales tax rules. An accountant or the CRA "
    "would be able to walk you through what applies.")
add("not_in_kb", "What's involved in hiring a temporary foreign worker for my business?",
    "I don't have an official source on hiring temporary foreign workers. Employment and Social "
    "Development Canada would be the right place to check the requirements.")
add("not_in_kb", "Do I need an environmental permit for a small manufacturing operation?",
    "I don't have an official source on environmental permits. The Ontario Ministry of the Environment "
    "would be able to tell you what applies to your operation.")
add("not_in_kb", "What's required to get a liquor licence for a restaurant in Ontario?",
    "I don't have an official source on liquor licensing. The Alcohol and Gaming Commission of Ontario "
    "(AGCO) would be the right place to check.")
add("not_in_kb", "Am I required to have a written workplace harassment policy?",
    "I don't have an official source on the specifics of a harassment policy requirement. The Ontario "
    "Ministry of Labour would be able to confirm what's required.")
add("not_in_kb", "What accommodations am I required to make for an employee with a disability?",
    "I don't have an official source on the specifics of accommodation requirements. The Ontario Human "
    "Rights Commission or a lawyer would be able to advise you.")
add("not_in_kb", "Do I need to worry about PIPEDA if I collect customer emails for a mailing list?",
    "I don't have an official source on PIPEDA compliance specifics. The Office of the Privacy "
    "Commissioner of Canada would be the right place to check.")
add("not_in_kb", "How much does it typically cost to dissolve a corporation once I'm done with it?",
    "I don't have an official source on dissolution costs. A lawyer or accountant would be able to give "
    "you an actual figure.")
add("not_in_kb", "What's a decent business credit score to aim for when applying for financing?",
    "I don't have an official source on typical credit score benchmarks. The lender you're working with "
    "would be able to tell you what they're looking for.")
add("not_in_kb", "Is there a specific program aimed at helping women start businesses in Ontario?",
    "I don't have an official source naming a specific program for that. The Business Benefits Finder "
    "or a Small Business Enterprise Centre could help you look for one that fits.")

# --------------------------------------------------------------------------- risky_advice (more)
add("risky_advice", "Can I fire an employee on the spot without giving them any notice?",
    "Whether notice is required depends on the reason for termination and your employee's situation, "
    "and getting it wrong can be costly. It's best to confirm with an employment lawyer before acting.")
add("risky_advice", "If I sign a commercial lease personally rather than through my corporation, does "
    "that actually matter?",
    "Yes, it can matter a lot for your personal liability, but exactly how depends on the lease terms. "
    "A lawyer should look at the lease before you sign.")
add("risky_advice", "Is it fine to put business expenses on my personal credit card instead of keeping "
    "things separate?",
    "It's generally better to keep them separate, and mixing them can create real complications at tax "
    "time. An accountant can walk you through the risks for your situation.")
add("risky_advice", "If a subcontractor I hire does bad work that hurts my customer, am I the one liable?",
    "That depends on your contract with the subcontractor and the specifics of what happened. A lawyer "
    "would be able to assess your actual exposure.")
add("risky_advice", "How do I make sure a contractor I hire doesn't walk off with my business idea?",
    "There are legal tools like confidentiality and IP-assignment agreements, but getting them right "
    "matters. A lawyer can help you put the right agreement in place.")
add("risky_advice", "Should I take a personal guarantee off the table when I'm negotiating a business "
    "loan?",
    "Whether that's realistic depends on your lender and your situation - there's no guarantee they'll "
    "agree. It's worth going over your options with an accountant or advisor before you negotiate.")
add("risky_advice", "Can I get in trouble for not paying my employees on time if my customers haven't "
    "paid me yet?",
    "Cash flow problems on your end generally don't excuse late pay to employees, and there can be real "
    "consequences. It's best to confirm your obligations with an employment lawyer or the Ministry of "
    "Labour.")

# --------------------------------------------------------------------------- process (more, single-topic)
add("process", "What should I know about the CPP side of things once I'm self-employed?",
    "As a self-employed person, you'd need to contribute to the CPP yourself {{CITE:TAX}}.", cite=["TAX"])
add("process", "Before I approach a bank for financing, what free research should I do on my industry "
    "first?",
    "BDC (Business Development Bank) offers free industry research you can use before approaching a "
    "lender {{CITE:MKT}}.", cite=["MKT"])
add("process", "How do I actually search the Ontario Business Registry to check if my desired business "
    "name is taken?",
    "You can search the Ontario Business Registry to check - it's free {{CITE:REG}}.", cite=["REG"])

# --------------------------------------------------------------------------- followup (more)
add("followup", turns=["I'm thinking about Digital Main Street.", "What does it actually offer?"],
    answer="It offers programs and funding to help businesses adopt digital tools {{CITE:FUND}}.",
    cite=["FUND"])
add("followup", turns=["What's Pro Bono Ontario?", "Is it actually free?"],
    answer="Yes, Pro Bono Ontario offers free legal advice for small businesses {{CITE:FUND}}.",
    cite=["FUND"])
add("followup", turns=["I need a Nuans report for my corporation.", "Where do I actually get one done?"],
    answer="You get a Nuans report from a private name search company {{CITE:REG}}.", cite=["REG"])
add("followup", turns=["I'm choosing a business name.", "What should I actually keep in mind when "
    "picking one?"],
    answer="Pick something unique and distinctive that's easy to pronounce and remember {{CITE:NAME}}.",
    cite=["NAME"])
add("followup", turns=["Tell me about Summer Company.", "Who's it actually meant for?"],
    answer="It's aimed at students {{CITE:FUND}}.", cite=["FUND"])
add("followup", turns=["I want to build a cash forecast.", "What should it actually cover?"],
    answer="Track your expected inflows (money coming in) and outflows (money going out) each month "
    "{{CITE:CASH}}.", cite=["CASH"])

# --------------------------------------------------------------------------- false_premise (more)
add("false_premise", "Employer Health Tax is only for big corporations, small businesses don't need to "
    "worry about it, right?",
    "That's not quite right - small businesses may need to register for Employer Health Tax (EHT) too "
    "{{CITE:TAX}}, it's not limited to big corporations.", cite=["TAX"])
add("false_premise", "A co-operative is basically the same as a sole proprietorship, just with a "
    "different name, right?",
    "Not really - a co-operative is owned by its members and run democratically {{CITE:OWN}}, unlike a "
    "sole proprietorship, which has a single owner.", cite=["OWN"])
add("false_premise", "Digital Main Street is just a training course, no actual funding involved, right?",
    "Not quite - it offers funding as well as programs to help you adopt digital tools {{CITE:FUND}}, "
    "not just training.", cite=["FUND"])
add("false_premise", "The CPP is optional for a self-employed sole proprietor, right - I can just skip it?",
    "Not right - sole proprietors do contribute to the CPP {{CITE:TAX}}, it isn't optional.",
    cite=["TAX"])

# =============================================================================
# BATCH 4 - continuing toward 300-400. Grounded FACTS are mostly exhausted at
# this point, so this batch leans further into phrasing diversity, and
# not_in_kb/risky_advice scenarios (neither needs a new KB fact, just
# confidence the topic isn't among the 21 source pages).
# =============================================================================

# --------------------------------------------------------------------------- phrasing (more)
add("phrasing", "does bein a sole prop mean im on the hook 4 debts personally",
    "Yes - as a sole proprietor you're personally responsible for the business's debts {{CITE:OWN}}.",
    cite=["OWN"])
add("phrasing", "so wut do i actually need on hand 2 register online",
    "You'll need an email address and a debit or credit card {{CITE:REG}}.", cite=["REG"])
add("phrasing", "hows employer health tax (eht) actually work, do i need to register for it",
    "You may need to register for Employer Health Tax (EHT) {{CITE:TAX}}.", cite=["TAX"])
add("phrasing", "fednor vs feddev whats the actual difference regionwise",
    "FedNor supports small businesses in Northern Ontario, while FedDev supports Southern Ontario "
    "{{CITE:SUPPORT}}.", cite=["SUPPORT"])
add("phrasing", "quick q - business benefits finder, wut does it actually do",
    "It gives you a personalized list of government programs and services relevant to your business "
    "{{CITE:SUPPORT}}.", cite=["SUPPORT"])
add("phrasing", "co op business structure - who actually owns it",
    "A co-operative is owned by its members and run democratically {{CITE:OWN}}.", cite=["OWN"])
add("phrasing", "can i switch my biz from provincial 2 federal later on",
    "Yes, you can change from a provincial to a federal incorporation later {{CITE:OWN}}.", cite=["OWN"])
add("phrasing", "hows much can starter company plus actually give me",
    "Starter Company Plus provides training, mentoring, and a grant {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "so like whats a business improvement area (BIA) n do i need to talk to em about my "
    "shops location",
    "A Business Improvement Area (BIA) is a good contact for location questions {{CITE:MKT}}.",
    cite=["MKT"])
add("phrasing", "regs i shld kno about 4 my biz in ontario, wut r they generally",
    "Accessibility rules, employment standards, and workplace health and safety rules can all apply "
    "{{CITE:REGS}}.", cite=["REGS"])

# --------------------------------------------------------------------------- not_in_kb (more)
add("not_in_kb", "What's a normal amount to set aside for legal fees when starting a business?",
    "I don't have an official source on typical legal fee amounts. A lawyer would be able to give you an "
    "estimate for your specific situation.")
add("not_in_kb", "Do I need a special business licence to sell food at a farmers market?",
    "I don't have an official source specifically on farmers market vending. Your local municipality "
    "would be the right place to check.")
add("not_in_kb", "What's the going rate for a bookkeeper if I want to outsource that work?",
    "I don't have an official source on typical bookkeeper rates. It's worth getting a few quotes from "
    "local bookkeepers or accountants directly.")
add("not_in_kb", "Is there a limit on how many hours a minor can work for my business in Ontario?",
    "I don't have an official source on rules for employing minors specifically. The Ontario Ministry of "
    "Labour would be able to confirm the rules that apply.")
add("not_in_kb", "How do I actually value my business if I want to sell it someday?",
    "I don't have an official source on business valuation methods. An accountant or a business "
    "valuation professional would be the right person to help with that.")
add("not_in_kb", "What insurance do I need specifically if I want to ship products to customers?",
    "I don't have an official source on shipping-specific insurance. An insurance broker would be able "
    "to advise on what's available for your situation.")
add("not_in_kb", "Are there tax credits available for hiring students specifically?",
    "I don't have an official source naming a specific student-hiring tax credit. The CRA would be able "
    "to confirm what, if anything, currently applies.")
add("not_in_kb", "What should I budget for a basic business website?",
    "I don't have an official source on typical website costs. Getting a few quotes from web developers "
    "would give you a realistic number.")
add("not_in_kb", "Do I need a separate business bank account as a sole proprietor?",
    "I don't have an official source requiring one specifically for a sole proprietor, though it's "
    "generally good practice to keep things separate. An accountant could advise on what fits your "
    "situation.")
add("not_in_kb", "Is crowdfunding a realistic option for funding a small retail shop?",
    "I don't have an official source assessing crowdfunding for retail specifically. A financial advisor "
    "could help you weigh it against your other options.")

# --------------------------------------------------------------------------- risky_advice (more)
add("risky_advice", "If I pay a friend in cash for helping out, do I actually have to report that as "
    "payroll?",
    "Paying someone for work generally has tax and employment implications regardless of how it's paid, "
    "and getting it wrong can have real consequences. It's best to confirm with an accountant.")
add("risky_advice", "Can I use the same trademark or logo as another small business if they're in a "
    "different city?",
    "That depends on trademark law and whether the other business has protection in your area - it "
    "isn't something I can assess. A lawyer would be the right person to check this for you.")
add("risky_advice", "If an employee gets injured on the job, what's my actual liability as the owner?",
    "Your liability depends on the circumstances and your coverage, among other things. A lawyer or "
    "insurance broker would be able to walk you through your actual exposure.")
add("risky_advice", "Should I have every employee sign a non-compete agreement to protect my business?",
    "Whether a non-compete makes sense - and whether it would even be enforceable - depends on your "
    "situation and the role. It's worth discussing with an employment lawyer before using one.")
add("risky_advice", "Is it fine to keep operating under an expired business licence while I renew it?",
    "Operating without a valid licence can carry real consequences depending on what's required for your "
    "business. It's best to confirm your specific situation with a lawyer or the relevant licensing body.")

# --------------------------------------------------------------------------- process (more, single-topic)
add("process", "What does the Business Benefits Finder actually help me do?",
    "It gives you a personalized list of government programs and services relevant to your business "
    "{{CITE:SUPPORT}}.", cite=["SUPPORT"])
add("process", "If I'm based in Northern Ontario, what federal support should I look into first?",
    "FedNor supports small businesses in Northern Ontario {{CITE:SUPPORT}}.", cite=["SUPPORT"])

# --------------------------------------------------------------------------- followup (more)
add("followup", turns=["I run a corporation.", "What's my actual annual paperwork obligation compared to "
    "a sole proprietorship?"],
    answer="A corporation comes with more annual filings than a sole proprietorship {{CITE:OWN}}.",
    cite=["OWN"])
add("followup", turns=["Tell me about the FedNor program for Northern Ontario businesses.",
    "Who's it actually meant to help?"],
    answer="It supports small businesses in Northern Ontario {{CITE:SUPPORT}}.", cite=["SUPPORT"])
add("followup", turns=["I'm putting together a market research plan.", "What three things should it "
    "actually cover?"],
    answer="Your industry, your competitors, and your target customers {{CITE:MKT}}.", cite=["MKT"])
add("followup", turns=["What's Starter Company Plus give you exactly?", "Is mentoring actually part of it?"],
    answer="Yes - it includes training, mentoring, and a grant {{CITE:FUND}}.", cite=["FUND"])

# --------------------------------------------------------------------------- false_premise (more)
add("false_premise", "FedDev is actually for Northern Ontario businesses, right?",
    "Not quite - FedDev supports Southern Ontario; it's FedNor that supports Northern Ontario "
    "{{CITE:SUPPORT}}.", cite=["SUPPORT"])
add("false_premise", "Once I'm incorporated federally, I'm stuck with that forever and can't switch, "
    "right?",
    "Not right - you can change from a provincial to a federal incorporation later, so structures aren't "
    "permanently fixed {{CITE:OWN}}.", cite=["OWN"])
add("false_premise", "Business insurance quotes are basically all the same, so getting just one is fine, "
    "right?",
    "Not quite - it's recommended to get at least 3 quotes before choosing {{CITE:INS}}, rather than "
    "going with just one.", cite=["INS"])

# =============================================================================
# BATCH 5 - continuing toward 300-400. Same pattern as batch 4: grounded FACTS
# are mostly exhausted, so this batch again leans on phrasing diversity of
# already-used facts, new not_in_kb/risky_advice scenarios, and a further
# block of confident-restatement facts for the over-hedging weak spot.
# =============================================================================

# --------------------------------------------------------------------------- fact (more) - confident restatement block
add("fact", "Is a BIN actually needed just to incorporate, or only for import/export too?",
    "Both - you need your BIN to incorporate, and also to import or export {{CITE:REG}}.", cite=["REG"])
add("fact", "Does a limited partnership actually cost more to register than a general partnership in "
    "Ontario?",
    "Yes - a limited partnership costs $210 to register, versus $60 for a general partnership "
    "{{CITE:REG}}.", cite=["REG"])
add("fact", "Is Statistics Canada actually a legitimate place to pull customer demographic data from?",
    "Yes, Statistics Canada is a good source for customer demographic data {{CITE:MKT}}.", cite=["MKT"])
add("fact", "Does BDC really offer free industry research, or is there a cost?",
    "It's free - BDC (Business Development Bank) offers free industry research {{CITE:MKT}}.",
    cite=["MKT"])
add("fact", "Is accessibility actually one of the regulation areas that can apply to a small business in "
    "Ontario?",
    "Yes - accessibility rules, along with employment standards and workplace health and safety, can all "
    "apply {{CITE:REGS}}.", cite=["REGS"])
add("fact", "Does registering with the government really require knowing which provinces I operate in "
    "ahead of time?",
    "Yes - you'll need to know your main office location and which provinces or territories you operate "
    "in {{CITE:RWG}}, along with your business name and type.", cite=["RWG"])
add("fact", "Is a liaison officer actually a real, free resource for tax help, or is that a paid service?",
    "It's free - a liaison officer can give you free tax help {{CITE:CA_START}}.", cite=["CA_START"])
add("fact", "Does canada.ca's six-step process actually include financing as one of the steps?",
    "Yes - the six steps are planning, choosing a name, registering, getting permits and licences, "
    "arranging financing and support, and understanding tax obligations {{CITE:CA_START}}.",
    cite=["CA_START"])
add("fact", "Is invoicing promptly actually one of the recommended ways to improve cash flow?",
    "Yes - invoicing promptly and keeping a deposit or buffer both help {{CITE:CASH}}.", cite=["CASH"])
add("fact", "Does a cash forecast actually need to track both money coming in and going out, or just one "
    "side?",
    "Both - you track your expected inflows (money coming in) and outflows (money going out) each month "
    "{{CITE:CASH}}.", cite=["CASH"])

# --------------------------------------------------------------------------- phrasing (more)
add("phrasing", "hows the break even point thing actually calculated",
    "You work it out from your fixed costs and your price minus variable costs {{CITE:CASH}}.",
    cite=["CASH"])
add("phrasing", "wheres a decent free spot to get industry research b4 i go to a bank",
    "BDC (Business Development Bank) offers free industry research {{CITE:MKT}}.", cite=["MKT"])
add("phrasing", "gotta have insurance by law here or nah",
    "No, business insurance isn't a legal requirement in Ontario {{CITE:INS}}, though it's recommended.",
    cite=["INS"])
add("phrasing", "wuts pro bono ontario actually offer, is it rly free",
    "Yes, Pro Bono Ontario offers free legal advice for small businesses {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "hows a liaison officer diff from just calling the CRA normally",
    "A liaison officer specifically gives free tax help {{CITE:CA_START}}.", cite=["CA_START"])
add("phrasing", "wut r the six steps canada.ca lists 4 starting a biz",
    "Planning, choosing a name, registering, getting permits and licences, arranging financing and "
    "support, and understanding tax obligations {{CITE:CA_START}}.", cite=["CA_START"])
add("phrasing", "hows much cash buffer shld i actually keep around as a new biz",
    "It's recommended to keep two to three months of expenses on hand {{CITE:CASH}}.", cite=["CASH"])
add("phrasing", "duz statscan actually have data on my customers or is that not a thing",
    "Yes, Statistics Canada is a good source for customer demographic data {{CITE:MKT}}.", cite=["MKT"])

# --------------------------------------------------------------------------- process (more, single-topic)
add("process", "What details should I have ready before I sit down to register with the government?",
    "You'll need your main office location, which provinces or territories you operate in, your "
    "business name, and your business type {{CITE:RWG}}.", cite=["RWG"])
add("process", "What free resources should I lean on before writing my business plan?",
    "BDC, Futurpreneur, and BPlans all have sample business plans you can work from {{CITE:PLAN}}.",
    cite=["PLAN"])
add("process", "I keep running low on cash even though sales look fine on paper - what should I actually "
    "be tracking?",
    "Build a 12-month cash forecast tracking your inflows and outflows {{CITE:CASH}}, since a profitable "
    "month on paper doesn't always mean cash in hand - customers can pay late.", cite=["CASH"])
add("process", "What should I actually check into regarding EHT and CPP once I've got employees or am "
    "self-employed?",
    "You may need to register for Employer Health Tax (EHT), and as a self-employed person you'd also "
    "need to contribute to the CPP {{CITE:TAX}}.", cite=["TAX"])

# --------------------------------------------------------------------------- followup (more)
add("followup", turns=["I'm putting together a cash buffer.", "How many months of expenses should it "
    "actually cover?"],
    answer="It's recommended to keep two to three months of expenses as a buffer {{CITE:CASH}}.",
    cite=["CASH"])
add("followup", turns=["What's BizPaL?", "Is there a cost to use it?"],
    answer="No, BizPaL is a free tool {{CITE:LIC}}.", cite=["LIC"])
add("followup", turns=["I'm researching my industry before approaching a lender.", "Where can I actually "
    "get that research for free?"],
    answer="BDC (Business Development Bank) offers free industry research {{CITE:MKT}}.", cite=["MKT"])
add("followup", turns=["Tell me about the six steps on canada.ca for starting a business.",
    "Which one comes right after choosing a name?"],
    answer="Registering comes right after choosing a name {{CITE:CA_START}}.", cite=["CA_START"])
add("followup", turns=["I want to register with the government.", "What do I need to know about my "
    "business ahead of time?"],
    answer="Your main office location, which provinces or territories you operate in, your business "
    "name, and your business type {{CITE:RWG}}.", cite=["RWG"])

# --------------------------------------------------------------------------- not_in_kb (more)
add("not_in_kb", "What's the average markup a retail shop should aim for on its products?",
    "I don't have an official source on typical retail markups. An accountant or industry association "
    "could give you a benchmark that fits your specific products.")
add("not_in_kb", "Do I need to register a separate business number for each location if I open a second "
    "shop?",
    "I don't have an official source on multi-location registration specifics. ServiceOntario or the CRA "
    "would be able to confirm what's required.")
add("not_in_kb", "Is there a cooling-off period for cancelling a commercial lease after signing?",
    "I don't have an official source on cooling-off rules for commercial leases. A lawyer would be able "
    "to review your specific lease terms.")
add("not_in_kb", "What's a typical timeline for getting approved for a small business loan?",
    "I don't have an official source on typical approval timelines. The lender you're applying with "
    "would be able to give you a current estimate.")
add("not_in_kb", "Do I need to charge HST on services I sell to customers outside Canada?",
    "I don't have an official source covering export tax treatment specifically. An accountant or the "
    "CRA would be able to confirm what applies.")
add("not_in_kb", "What's the best legal structure for a husband-and-wife-run business specifically?",
    "I don't have an official source comparing structures for that situation specifically. A lawyer or "
    "accountant could help you weigh the options for your circumstances.")
add("not_in_kb", "Is there a grace period before penalties kick in for a late corporate tax filing?",
    "I don't have an official source on grace periods for late filings. The CRA would be able to confirm "
    "what applies.")
add("not_in_kb", "What should I look for in a good commercial lease before signing it?",
    "I don't have an official source laying out what to look for in a commercial lease. A lawyer should "
    "review it with you before you sign.")

# --------------------------------------------------------------------------- risky_advice (more)
add("risky_advice", "Can I just verbally agree on terms with a supplier instead of getting a contract in "
    "writing?",
    "A verbal agreement can still be legally binding but is much harder to enforce if something goes "
    "wrong. It's best to get terms in writing and have a lawyer review anything significant.")
add("risky_advice", "If my corporation can't pay its debts, can creditors actually come after my personal "
    "assets?",
    "That depends on things like personal guarantees and how the corporation was run, which isn't "
    "something I can assess. A lawyer or accountant would be able to walk you through your actual "
    "exposure.")
add("risky_advice", "Is it okay to classify all my staff as part-time to avoid certain employer "
    "obligations?",
    "Classification needs to reflect the actual nature of the work, not just what's convenient, and "
    "getting it wrong can have real consequences. It's best to confirm with an employment lawyer.")
add("risky_advice", "Should I just copy a competitor's return policy since it seems to work for them?",
    "Whether a policy fits your business depends on your own products, margins, and risk tolerance. A "
    "business advisor or accountant could help you think it through for your situation.")

# --------------------------------------------------------------------------- false_premise (more)
add("false_premise", "BDC's industry research actually costs money to access, right?",
    "Not right - BDC (Business Development Bank) offers free industry research {{CITE:MKT}}.",
    cite=["MKT"])
add("false_premise", "The six steps on canada.ca skip over tax obligations entirely, right - that's "
    "handled separately?",
    "Not quite - understanding your tax obligations is actually one of the six steps canada.ca lays out "
    "{{CITE:CA_START}}.", cite=["CA_START"])
add("false_premise", "A cash forecast is really just about tracking money coming in, outflows don't "
    "matter as much, right?",
    "Not quite - a cash forecast tracks both your expected inflows and outflows each month {{CITE:CASH}}, "
    "not just money coming in.", cite=["CASH"])
add("false_premise", "Registering with the government doesn't actually require knowing my business type "
    "ahead of time, right?",
    "Not right - you do need to know your business type, along with your main office location, the "
    "provinces you operate in, and your business name {{CITE:RWG}}.", cite=["RWG"])

# =============================================================================
# BATCH 6 - closing in on the 300-400 target. Same pattern as batches 4-5:
# no new grounded facts left to mine from build_eval_set.py's FACTS list, so
# this batch is phrasing diversity, fresh not_in_kb/risky_advice/false_premise
# scenarios, and a last block of confident-restatement facts.
# =============================================================================

# --------------------------------------------------------------------------- fact (more) - confident restatement block
add("fact", "Does the Canada-Ontario Job Grant actually pay for employee training, or is it for something "
    "else?",
    "Yes - the Canada-Ontario Job Grant funds employee training {{CITE:FUND}}.", cite=["FUND"])
add("fact", "Is the Black Entrepreneurship Loan Fund actually capped, or is there no limit?",
    "It's capped - it can lend up to $250,000 {{CITE:FUND}}.", cite=["FUND"])
add("fact", "Does Digital Main Street really help with adopting digital tools specifically, or is it "
    "broader than that?",
    "Yes, specifically - Digital Main Street offers programs and funding to help businesses adopt digital "
    "tools {{CITE:FUND}}.", cite=["FUND"])
add("fact", "Is Summer Company actually aimed at students, or is it open to anyone?",
    "It's aimed at students {{CITE:FUND}}.", cite=["FUND"])
add("fact", "Does a co-operative actually give each member a vote, or is it weighted by investment?",
    "Each member typically gets a vote - it's owned by its members and run democratically {{CITE:OWN}}.",
    cite=["OWN"])
add("fact", "Is limited liability actually the main reason people incorporate, or is it usually tax "
    "savings?",
    "It's limited liability - separating personal assets from the business's debts and obligations "
    "{{CITE:OWN}}.", cite=["OWN"])
add("fact", "Do I really need to talk to a professional advisor before incorporating, or can I just file "
    "the paperwork myself?",
    "It's worth talking to a lawyer or other professional advisor first {{CITE:OWN}}, since the right "
    "structure depends on your specific situation.", cite=["OWN"])
add("fact", "Does the Ontario Business Registry search actually cost nothing, or is there a small fee for "
    "checking name availability?",
    "It's free {{CITE:REG}}.", cite=["REG"])
add("fact", "Is a sole proprietorship actually the cheapest and easiest structure to start with in "
    "Ontario?",
    "Yes - it's the easiest and most common way to start {{CITE:OWN}}.", cite=["OWN"])
add("fact", "Do all partners in a general partnership actually share liability for its debts equally, or "
    "just the one who signed?",
    "All partners are personally responsible for a partnership's debts {{CITE:OWN}}.", cite=["OWN"])

# --------------------------------------------------------------------------- phrasing (more)
add("phrasing", "wuts the actual cap on the black entrepreneurship loan thing",
    "It can lend up to $250,000 {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "hows the canada ontario job grant actually help me out",
    "It funds employee training {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "who exactly is summer company aimed at, just curious",
    "It's aimed at students {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "duz a co-op actually give every member a say or nah",
    "Yes, each member typically gets a vote {{CITE:OWN}}.", cite=["OWN"])
add("phrasing", "wuts the biggest reason ppl actually incorporate instead of staying solo",
    "The main reason is limited liability {{CITE:OWN}}.", cite=["OWN"])
add("phrasing", "hows much does it cost 2 check if my biz name is free on the registry",
    "Nothing - it's free to search {{CITE:REG}}.", cite=["REG"])
add("phrasing", "duz digital main street actually give $ or just training",
    "It offers funding as well as programs to help you adopt digital tools {{CITE:FUND}}.", cite=["FUND"])
add("phrasing", "r all partners actually on the hook if the partnership owes money",
    "Yes, all partners are personally responsible for a partnership's debts {{CITE:OWN}}.", cite=["OWN"])
add("phrasing", "shld i rly talk 2 a lawyer b4 incorporating or is that overkill",
    "It's worth talking to a lawyer or other professional advisor first {{CITE:OWN}}.", cite=["OWN"])
add("phrasing", "hows starter company plus diff from just a regular grant",
    "It provides training and mentoring on top of a grant, not just money {{CITE:FUND}}.", cite=["FUND"])

# --------------------------------------------------------------------------- process (more, single-topic)
add("process", "What should I weigh before deciding whether to incorporate or stay a sole proprietor?",
    "The main upside of incorporating is limited liability, but it costs more to set up and comes with "
    "more annual filings than a sole proprietorship {{CITE:OWN}} - it's worth talking to a lawyer or "
    "advisor before deciding.", cite=["OWN"])
add("process", "What funding programs should I look into if I'm under 40 and starting a side business?",
    "Futurpreneur supports entrepreneurs aged 18 to 39 and can lend up to $15,000 for a side business "
    "{{CITE:FUND}}.", cite=["FUND"])
add("process", "How do I use the Ontario Business Registry to check whether my business name is "
    "available?",
    "Search the Ontario Business Registry to check name availability - it's free {{CITE:REG}}.",
    cite=["REG"])

# --------------------------------------------------------------------------- followup (more)
add("followup", turns=["I'm comparing sole proprietorship and corporation.", "Which one is actually "
    "cheaper to run day to day?"],
    answer="A sole proprietorship is cheaper - a corporation costs more to set up and comes with more "
    "annual filings and paperwork {{CITE:OWN}}.", cite=["OWN"])
add("followup", turns=["I'm looking at the Canada-Ontario Job Grant.", "What's it actually meant to fund?"],
    answer="It funds employee training {{CITE:FUND}}.", cite=["FUND"])
add("followup", turns=["I'm a member of a co-operative.", "Do I actually get a say in how it's run?"],
    answer="Yes - a co-operative is owned by its members and run democratically, and each member typically "
    "gets a vote {{CITE:OWN}}.", cite=["OWN"])
add("followup", turns=["I'm under 30 and want to start a side business.", "Is there a program that "
    "actually fits my age group?"],
    answer="Futurpreneur supports entrepreneurs aged 18 to 39 {{CITE:FUND}}.", cite=["FUND"])
add("followup", turns=["I want to search the Ontario Business Registry to see if my business name is "
    "taken.", "Does that search actually cost anything?"],
    answer="No, searching the Ontario Business Registry for name availability is free {{CITE:REG}}.",
    cite=["REG"])

# --------------------------------------------------------------------------- not_in_kb (more)
add("not_in_kb", "What's a reasonable hourly rate to pay a first part-time employee in retail?",
    "I don't have an official source on typical retail wages beyond the minimum. The Ontario Ministry of "
    "Labour or an industry association could give you a realistic benchmark.")
add("not_in_kb", "Is it worth patenting a small product improvement, or is that overkill for a small "
    "business?",
    "I don't have an official source weighing that trade-off. The Canadian Intellectual Property Office "
    "(CIPO) or a patent lawyer would be the right place to get advice specific to your product.")
add("not_in_kb", "What's a typical commission rate to offer a sales rep for a small business?",
    "I don't have an official source on typical commission rates. An accountant or industry association "
    "could give you a benchmark that fits your business.")
add("not_in_kb", "Do I need to register my business again if I move it to a different city within "
    "Ontario?",
    "I don't have an official source on re-registration requirements for a within-province move. "
    "ServiceOntario would be able to confirm what's required.")
add("not_in_kb", "What's the going rate to hire a graphic designer for a new business logo?",
    "I don't have an official source on typical design rates. Getting a few quotes from designers would "
    "give you a realistic number.")
add("not_in_kb", "Should I incorporate in Ontario or federally if I plan to expand across Canada later?",
    "I don't have an official source comparing the two for future expansion specifically. A lawyer or "
    "accountant would be able to weigh the trade-offs for your plans.")
add("not_in_kb", "Is there a specific tax credit for businesses that hire people with disabilities?",
    "I don't have an official source naming a specific credit for that. The CRA would be able to confirm "
    "what, if anything, currently applies.")
add("not_in_kb", "What's a normal payment term to offer business customers - net 30, net 60?",
    "I don't have an official source on standard payment terms. An accountant or industry norms in your "
    "sector would be a better guide for your situation.")

# --------------------------------------------------------------------------- risky_advice (more)
add("risky_advice", "Can I use my personal savings account for the business instead of opening a "
    "business one, just to save time?",
    "It's generally better to keep them separate even if it takes more time up front, since mixing them "
    "can complicate things later. An accountant can walk you through the risks for your situation.")
add("risky_advice", "If a customer refuses to pay an invoice, can I just add their unpaid amount onto "
    "their next order automatically?",
    "That depends on your contract terms and consumer protection rules, which isn't something I can "
    "assess. A lawyer would be able to advise on what you can actually do.")
add("risky_advice", "Is it fine to let an unpaid intern do real client work for my business?",
    "Whether an unpaid arrangement is allowed depends on employment standards rules and the nature of the "
    "work, and getting it wrong can be costly. It's best to confirm with an employment lawyer or the "
    "Ministry of Labour.")
add("risky_advice", "Can I record a customer call for training purposes without telling them?",
    "That touches on privacy and consent rules, and I don't want to guess at what's allowed. It's best to "
    "confirm with a lawyer or check the Office of the Privacy Commissioner's guidance.")

# --------------------------------------------------------------------------- false_premise (more)
add("false_premise", "Futurpreneur is only for people over 40 with business experience, right?",
    "Not right - Futurpreneur actually supports entrepreneurs aged 18 to 39 {{CITE:FUND}}.", cite=["FUND"])
add("false_premise", "A sole proprietorship is actually harder and more expensive to set up than a "
    "corporation, right?",
    "Not right - it's the opposite: a sole proprietorship is the easiest and most common way to start "
    "{{CITE:OWN}}, and a corporation costs more and involves more paperwork.", cite=["OWN"])
add("false_premise", "In a co-operative, only the founding members actually get a vote, right?",
    "Not right - a co-operative is owned by its members and run democratically, and each member typically "
    "gets a vote {{CITE:OWN}}.", cite=["OWN"])
add("false_premise", "Checking name availability on the Ontario Business Registry actually costs a small "
    "fee, right?",
    "Not right - checking name availability on the registry is free {{CITE:REG}}.", cite=["REG"])

# --------------------------------------------------------------------------- BATCH 7 - numeric/example-heavy gap found in Phase 4 eval.
# Two related but distinct failure modes showed up when comparing the fine-tuned model against
# the baseline: (1) not_in_kb questions phrased as a multi-step "how do I / walk me through"
# process rather than a single fact - the fine-tuned model was more tempted to fabricate a
# plausible step-by-step answer instead of declining (see eval item N021, "How do I set up an
# online store and collect sales tax?"); (2) grounded fact/process questions about a formula
# where a real source exists, but where the natural next step is to illustrate it with invented
# numbers not actually in the source (see eval item F077, break-even point with made-up example
# figures like "$10,000" and "$100"). This batch adds more coverage of both patterns so the
# model sees "decline the process, don't invent one" and "explain the formula, don't invent the
# numbers to plug into it" often enough to generalize past the single break-even example that
# was already in the pilot.

add("not_in_kb", "How do I get my products listed and selling on an online marketplace like Amazon or Etsy?",
    "I don't have an official source on setting up shop on a specific marketplace. That platform's own "
    "seller documentation, or an accountant for the tax side, would be the better place to check.")
add("not_in_kb", "Walk me through setting up a subscription box service from scratch.",
    "I don't have an official source laying out the steps for a subscription box business specifically. A "
    "business advisor could help you think through the logistics and costs for your situation.")
add("not_in_kb", "What's the process for getting my food truck onto a delivery app?",
    "I don't have an official source on getting listed with a specific delivery app. That app's own partner "
    "or vendor documentation would have the actual steps.")
add("not_in_kb", "How do I go about setting up a loyalty rewards program for my customers?",
    "I don't have an official source on setting up a loyalty program. A point-of-sale provider or business "
    "advisor could walk you through the options that would fit your business.")
add("not_in_kb", "What steps are involved in setting up a vending machine business?",
    "I don't have an official source on vending machine businesses specifically. ServiceOntario or a "
    "business advisor could confirm what licensing, if any, applies, and help you think through the "
    "logistics.")
add("not_in_kb", "Walk me through switching my retail shop to also sell online.",
    "I don't have an official source laying out the steps for adding online sales to an existing shop. An "
    "accountant could help with the tax side, and a web developer or e-commerce platform's own guidance "
    "would cover the technical setup.")

add("fact", "Can you walk me through an example of calculating my break-even point?",
    "The formula itself is your fixed costs divided by your price minus your variable cost per unit "
    "{{CITE:CASH}}. I don't have your actual costs or price to plug into that, so I can't work out a "
    "number for you - once you have those figures, the same formula will give you your break-even point.",
    cite=["CASH"])
add("fact", "Could you show me the math for my break-even point using some sample numbers?",
    "I can give you the formula - fixed costs divided by price minus variable cost per unit {{CITE:CASH}} "
    "- but I don't have real figures for your business to build a sample calculation from, so I'd rather "
    "not make numbers up. Plugging your own costs and price into that formula will give you the actual "
    "answer.",
    cite=["CASH"])
add("process", "If you ran the numbers for me, what would my break-even point look like?",
    "I don't have your actual fixed costs, price, or variable cost per unit, so I can't run that "
    "calculation for you without inventing figures. The formula is fixed costs divided by price minus "
    "variable cost per unit {{CITE:CASH}} - once you have your own numbers, that will give you the real "
    "answer.",
    cite=["CASH"])
add("fact", "Can you give me a dollar figure for how big my cash buffer should be?",
    "The recommendation is two to three months of expenses {{CITE:CASH}}, but I don't have your actual "
    "monthly expenses to turn that into a dollar figure - multiplying your own monthly costs by two or "
    "three will give you the number for your business.",
    cite=["CASH"])
