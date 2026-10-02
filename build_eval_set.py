"""Generates data/eval/eval_set.jsonl (the Phase 2 evaluation set) from the compact
tables below. Every "fact" question is written from what the saved pages actually say,
so a correct answer can be checked automatically. Edit this file and re-run to change
the set:

    python build_eval_set.py

Item format (one JSON object per line):
  id, category, expect, turns (list of user messages; the LAST one is scored),
  expected_facts  : list of groups; a group is a list of alternatives (any-of, case-insensitive);
                    ALL groups must appear in the answer
  expected_sources: URL fragments; at least one must be among the sources shown
                    (a full https:// URL must match exactly)
  forbidden       : strings that must NOT appear in the answer
  expect values   : answer | no_source_general | decline | refer_professional
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "data" / "eval" / "eval_set.jsonl"

# Short names for the pages a good answer should draw on.
HST = ["confirm-hst", "gst-hst-businesses"]
REG = ["register-your-business-online"]
OWN = ["decide-ownership-structure"]
MKT = ["conduct-market-research"]
PLAN = ["prepare-business-plan"]
LIC = ["check-licences-permits"]
TAX = ["tax-obligations"]
INS = ["business-insurance"]
REGS = ["understand-regulations"]
FUND = ["get-funding-or-more-help"]
ON_START = ["https://www.ontario.ca/page/business/start"]
CA_START = ["https://www.canada.ca/en/services/business/start.html"]
NAME = ["choosing-a-business-name"]
RWG = ["register-with-gov"]
SUPPORT = ["support-financing"]
CASH = ["cash flow basics"]  # matched against the title of your own document (it has no URL)
FOOD = ["food-handler-training-and-certification"]
ESA = ["guide-employment-standards-act-0"]
STARTCOST = ["business-start-costs"]
CHECKLIST = ["checklist-small-businesses"]


def F(*groups):
    """F("a|b", "c") -> [["a","b"],["c"]]  (each group = alternatives, all groups required)."""
    return [g.split("|") for g in groups]


items: list[dict] = []


def add(category, expect, question, facts=None, sources=None, forbidden=None, turns=None):
    items.append(
        {
            "category": category,
            "expect": expect,
            "turns": turns or [question],
            "expected_facts": facts or [],
            "expected_sources": sources or [],
            "forbidden": forbidden or [],
        }
    )


NOT_ACCEPTED = ("not be accepted|not accepted|isn't accepted|won't be accepted|cannot be used|can't be used|"
                "will not be accepted|cannot use|can't use|not able to use|unable to use")
NOT_MANDATORY = "not mandatory|isn't mandatory|is not mandatory|not required|isn't required|is not required"

# --------------------------------------------------------------------------- fact lookups
FACTS = [
    ("At what revenue level do I have to start charging HST?", F("30,000"), HST),
    ("How many consecutive calendar quarters does the HST revenue test look at?", F("four"), HST),
    ("What counts as a calendar quarter for the GST/HST test?", F("three months|3 months", "january"), HST),
    ("How much does it cost to register a sole proprietorship in Ontario?", F("$60"), REG),
    ("What is the registration fee for a business corporation in Ontario?", F("$300"), REG),
    ("How much is it to register an Ontario limited partnership?", F("$210"), REG),
    ("What does a general partnership registration cost in Ontario?", F("$60"), REG),
    ("Do I need a Nuans report to register a corporation in Ontario?", F("nuans", "number name|reserve|name search"), REG),
    ("Can I use a federal Nuans search for an Ontario corporation?", F(NOT_ACCEPTED), REG),
    ("Where do I get a Nuans name search report?", F("private name search company|private company|name search company"), REG),
    ("What do I need in order to register a business online in Ontario?", F("email", "debit|credit card"), REG),
    ("Where do I register my business in Ontario?", F("Ontario Business Registry"), REG),
    ("What is an Ontario Business Identification Number?", F("BIN|Business Identification Number", "ServiceOntario"), REG),
    ("How many digits does the Ontario BIN have?", F("9|nine"), REG),
    ("Is the Ontario BIN the same as the CRA business number?", F("different|not the same", "BN|business number"), REG),
    ("What do I need the BIN for?", F("incorporate", "import|export"), REG),
    ("How do I check if my business name is already taken in Ontario?", F("Ontario Business Registry", "free|search"), REG),
    ("Is searching for a business name in the Ontario Business Registry free?", F("free"), REG),
    ("Do I need an account to register my business online in Ontario?", F("login", "business account"), REG),
    ("Who has to register with the Ontario Business Registry?", F("employees", "facilities|offices"), REG),
    ("Do I have to register a sole proprietorship in Ontario?", F("own name|your own name"), OWN),
    ("What are the four types of business structures in Ontario?", F("sole proprietorship", "partnership", "corporation", "co-operative|cooperative"), OWN),
    ("What is the easiest and most common way to start a business in Ontario?", F("sole proprietorship"), OWN),
    ("What are the advantages of a sole proprietorship?", F("easy|affordable", "profits|control"), OWN),
    ("What are the downsides of being a sole proprietor?", F("debts", "personal"), OWN),
    ("Are partners personally responsible for a partnership's debts?", F("all partners", "debts"), OWN),
    ("What is the main benefit of incorporating?", F("limited liability"), OWN),
    ("What are the drawbacks of setting up a corporation?", F("costs more|cost more|more expensive|more to set up", "annual filings|filings|records|complex"), OWN),
    ("Is my business name protected if I incorporate federally?", F("protected", "federal"), OWN),
    ("Who should I talk to before I incorporate?", F("lawyer|professional advisor|advisor"), OWN),
    ("What is a co-operative?", F("members", "one member|democratic|vote"), OWN),
    ("Can I switch from provincial to federal incorporation later?", F("change|switch", "federal"), OWN),
    ("How many Small Business Enterprise Centres are there in Ontario?", F("47"), ON_START),
    ("What help do Small Business Enterprise Centres provide?", F("advisory|workshops|training|mentorship"), ON_START + FUND),
    ("Who do Regional Innovation Centres help?", F("innovation|technology"), ON_START + FUND),
    ("What is BizPaL?", F("free", "licences|permits|licenses"), LIC),
    ("How do I find out which licences and permits my business needs?", F("BizPaL"), LIC),
    ("Which levels of government might require licences or permits for my business?", F("federal", "provincial", "municipal"), LIC),
    ("Is business insurance mandatory in Ontario?", F(NOT_MANDATORY, "recommended"), INS),
    ("Do I need insurance if I work from home?", F("recommended", "home"), INS),
    ("How many insurance quotes should I get?", F("3|three"), INS),
    ("Who do I contact to buy business insurance?", F("agent|broker"), INS),
    ("What does business insurance protect?", F("propert", "operations|income"), INS),
    ("What taxes does a self-employed person in Ontario need to think about?", F("personal income", "CPP|Canada Pension Plan"), TAX),
    ("Do sole proprietors contribute to the CPP?", F("CPP|Canada Pension Plan"), TAX),
    ("Do I need to register for Employer Health Tax?", F("Employer Health Tax|EHT"), TAX),
    ("Where can I get free legal advice for my small business?", F("Pro Bono Ontario"), FUND),
    ("What is Starter Company Plus?", F("training|mentoring|grant"), FUND),
    ("How much can I borrow through Futurpreneur for a side business?", F("15,000"), FUND),
    ("What age group does Futurpreneur Canada support?", F("18", "39"), FUND),
    ("What is the Summer Company program?", F("student"), FUND),
    ("How much can the Black Entrepreneurship Loan Fund lend?", F("250,000"), FUND),
    ("What is the Canada-Ontario Job Grant?", F("training"), FUND),
    ("Is there funding for Indigenous entrepreneurs in Ontario?", F("Indigenous|First Nations", "Indigenous Entrepreneurship Startup Program|Indian Agricultural Program|Waubetek|Nishnawbe|R.A.I.S.E"), FUND),
    ("What is Digital Main Street?", F("programs|funding", "digital"), FUND),
    ("Is there a grant to help me adopt digital tools?", F("grant", "digital"), FUND),
    ("What should my market research cover?", F("industry", "competitors", "customer|target market"), MKT),
    ("Where can I get free industry research?", F("BDC|Business Development"), MKT),
    ("Where do I find data about my customers' demographics?", F("Statistics Canada"), MKT),
    ("Who should I contact about the location for my business?", F("Business Improvement|BIA"), MKT),
    ("What start-up costs should I research?", F("registration|marketing|advertising|licensing|insurance|rent", "utilities|web site|website|product development"), MKT),
    ("What should a business plan explain?", F("idea", "goals", "resources"), PLAN),
    ("Where can I find sample business plans?", F("BDC|Futurpreneur|BPlans"), PLAN),
    ("What regulations might apply to my business in Ontario?", F("accessibility", "employment standards", "health and safety|workplace health"), REGS),
    ("What are the steps to start a business in Ontario?", F("market research", "business plan", "register", "insurance"), ON_START),
    ("What are the six steps to starting a business on Canada.ca?", F("planning", "name", "register|registering", "permits|licences", "financing|support", "tax"), CA_START),
    ("What should I think about when choosing a business name?", F("unique|distinctive", "easy to pronounce|remember"), NAME),
    ("What do I need to know before registering my business with the government?", F("main office", "provinces|territories", "name", "type of business|business type"), RWG),
    ("What business types can I choose from when registering?", F("corporation", "sole proprietorship|partnership", "cooperative|co-operative"), RWG),
    ("What federal support is there for small businesses in Northern Ontario?", F("FedNor"), SUPPORT),
    ("What federal support is there for small businesses in Southern Ontario?", F("FedDev"), SUPPORT),
    ("What is the Business Benefits Finder?", F("personalized|list of programs|programs and services"), SUPPORT),
    ("I have a temporary SIN starting with 9. How do I register for GST/HST?", F("Business Registration Online|BRO"), ["gst-hst-businesses"]),
    ("Do I have to file my GST/HST returns electronically?", F("2024", "electronic"), ["gst-hst-businesses"]),
    ("Can I get free tax help for my business?", F("liaison officer|free tax help"), CA_START),
    ("Why can a profitable business still run out of cash?", F("paid|customers|late", "cash"), CASH),
    ("How do I work out my break-even point?", F("fixed", "price|variable"), CASH),
    ("How big a cash buffer should I keep?", F("two to three months|2-3 months|three months"), CASH),
    ("How do I build a 12-month cash forecast?", F("inflows|coming in|money in", "outflows|going out|money out"), CASH),
    ("What can I do to improve my cash flow?", F("invoice", "deposit|buffer"), CASH),
    ("Does a bakery need a certified food handler on site?", F("certified food handler", "every hour|at all times|operates"), FOOD),
    ("Is there a fee to become a recognized food handler certification provider?", F("no fee"), FOOD),
    ("How much vacation pay do I owe an employee who has worked less than five years?", F("2 weeks|two weeks", "4%"), ESA),
    ("How much vacation time and pay does an employee get after five years?", F("3 weeks|three weeks"), ESA),
    ("How soon after hiring someone do I have to give them the employment standards poster?", F("30 days"), ESA),
    ("When does a start-up expense become tax deductible?", F("carried on a business"), STARTCOST),
    ("How much vacation pay do I owe my employees?", F("4%", "6%"), ESA),
]
for q, facts, src in FACTS:
    add("fact", "answer", q, facts, src)

# --------------------------------------------------------------------------- casual / messy phrasing
PHRASING = [
    ("hst when do i start charging it??", F("30,000"), HST),
    ("how much 2 register sole prop in ontario", F("$60"), REG),
    ("do i need insurance for my home business", F("recommended"), INS),
    ("what's a nuans", F("nuans", "name"), REG),
    ("where do i get money to start a small biz in ontario", F("Futurpreneur|Starter Company|grant|loan|funding"), FUND),
    ("is there a free tool to see what permits i need", F("BizPaL"), LIC),
    ("whats bizpal", F("free", "licences|permits"), LIC + ON_START + CA_START),
    ("futurpreneur??", F("loan|financing"), FUND),
    ("what is a bin number for my business", F("9|nine|identification"), REG),
    ("digital main street", F("programs|funding"), FUND),
]
for q, facts, src in PHRASING:
    add("phrasing", "answer", q, facts, src)

# --------------------------------------------------------------------------- multi-step / process
PROCESS = [
    ("I want to start a small bakery in Ontario. What are the first steps?", F("market research", "business plan", "ownership|structure", "register"), ON_START + ["conduct-market-research", "prepare-business-plan"]),
    ("I'm a freelance designer. What do I need to do to set up as a sole proprietor?", F("own name|your own name", "CPP|personal income"), OWN + TAX),
    ("Walk me through registering a corporation in Ontario.", F("Ontario Business Registry", "nuans", "$300"), REG),
    ("What are the steps to register a partnership online in Ontario?", F("Ontario Business Registry", "$60", "login|account"), REG),
    ("I'm starting a home-based business. What should I know about insurance, licences and tax?", F("insurance", "BizPaL|licences", "HST|CPP|personal income"), INS + LIC + TAX),
    ("I'm a student who wants to run a summer business. What help exists?", F("Summer Company"), FUND),
    ("I'm 25 and want to start a business. What funding is out there?", F("Futurpreneur"), FUND),
    ("What should I sort out before I hire my first employee in Ontario?", F("employment standards|Employer Health Tax|health and safety"), REGS + TAX),
    ("How do I decide between a sole proprietorship and a corporation?", F("limited liability", "personal assets|debts", "lawyer|advisor|accountant"), OWN),
    ("What do I have to do to charge HST correctly?", F("30,000", "GST/HST account|register"), HST),
    ("Give me a checklist for launching a coffee shop in Ontario.", F("market research", "register", "licences|permits", "insurance"), ON_START),
    ("What costs should I plan for when starting a business?", F("registration", "insurance", "rent|marketing|licensing"), MKT),
]
for q, facts, src in PROCESS:
    add("process", "answer", q, facts, src)

# --------------------------------------------------------------------------- multi-turn follow-ups
FOLLOWUPS = [
    (["When do I have to start charging HST?", "Yes, I made $35,000 over the last four quarters. What should I do next?"], F("register|GST/HST account", "30,000|threshold"), HST),
    (["I want to register a corporation in Ontario.", "How much does that cost?"], F("$300"), REG),
    (["Tell me about sole proprietorships.", "What are the downsides?"], F("debts", "personal"), OWN),
    (["What business structures can I choose from?", "Which one protects my personal assets?"], F("corporation", "liability"), OWN),
    (["I'm starting a landscaping business.", "Do I need any licences?"], F("BizPaL"), LIC),
    (["How do I register a business name?", "And is checking availability free?"], F("free"), REG),
    (["Is business insurance required?", "How many quotes should I get?"], F("3|three"), INS),
    (["I'm 30 and want to start a business.", "Is there any loan for me?"], F("Futurpreneur", "15,000"), FUND),
    (["What is the Ontario BIN?", "Is it the same as a CRA business number?"], F("different|not the same"), REG),
    (["I'm a student.", "Is there a program to help me start a summer business?"], F("Summer Company"), FUND),
    (["Tell me about co-operatives.", "How are decisions made?"], F("one member|democratic|vote"), OWN),
    (["What is a Nuans report?", "Who do I order it from?"], F("private"), REG),
    (["I'm self-employed.", "What taxes do I have to think about?"], F("personal income", "CPP|Canada Pension Plan"), TAX),
    (["When do I have to charge HST?", "Actually, what is the registration fee for a sole proprietorship?"], F("$60"), REG),
    (["I have a temporary SIN starting with 9.", "How do I get a GST/HST number?"], F("Business Registration Online|BRO"), ["gst-hst-businesses"]),
]
for turns, facts, src in FOLLOWUPS:
    add("followup", "answer", turns[-1], facts, src, turns=turns)

# --------------------------------------------------------------------------- in scope, but NOT in the knowledge base
NOT_IN_KB = [
    "What is the minimum wage in Ontario?",
    "What is WSIB and do I need to register?",
    "How do I trademark my business name?",
    "What food handler certification does a bakery need?",
    "Do I need a health inspection to open a restaurant?",
    "What is the difference between cash and accrual accounting?",
    "Which accounting software should I use for my small business?",
    "How do I write a marketing plan?",
    "How can I get more customers using social media?",
    "When is my corporate tax return due?",
    "How often do I have to file my HST return?",
    "What is the current HST rate in Ontario?",
    "How do I set up payroll for my first employee?",
    "What is the difference between an employee and an independent contractor?",
    "How do I negotiate a commercial lease?",
    "What interest rate should I expect on a small business loan?",
    "Can I raise money for my business through crowdfunding?",
    "What is the SR&ED tax credit?",
    "How much does it cost to incorporate federally?",
    "Do I need a separate business bank account?",
    "How do I set up an online store and collect sales tax?",
    "What permits does a food truck need in Toronto?",
    "How do I protect my invention with a patent?",
    "What should go in a partnership agreement?",
    "How do I apply for a bank loan for my business?",
    "How much should I charge as a freelancer?",
    "How do I export my products to the United States?",
    "How do I close down my business properly?",
    "What are good ways to advertise a new local business?",
    "How do I register for payroll deductions with the CRA?",
    "Do I need a zoning permit to run a business from my home in London, Ontario?",
    "What is the small business exemption amount for Employer Health Tax?",
    "How do I get a business credit card?",
    "What software can I use to build a website for my business?",
]
for q in NOT_IN_KB:
    add("not_in_kb", "no_source_general", q)

# --------------------------------------------------------------------------- off topic (should politely decline)
OFF_TOPIC = [
    ("What is the capital of France?", ["Paris"]),
    ("Write me a poem about the ocean.", ["waves"]),
    ("What is 15 times 12?", ["180"]),
    ("Give me a recipe for lasagna.", ["mozzarella", "ricotta", "noodles"]),
    ("Who won the Stanley Cup last year?", ["won the"]),
    ("What's the weather going to be in London, Ontario tomorrow?", ["degrees"]),
    ("Write a Python function to reverse a string.", ["def ", "return"]),
    ("Recommend a good movie for tonight.", ["starring"]),
    ("How do I fix a leaking tap?", ["washer", "wrench"]),
    ("Tell me a joke.", ["why did"]),
    ("What should I take for a headache?", ["ibuprofen", "acetaminophen", "tylenol"]),
    ("Which stocks should I buy this month?", ["shares of"]),
    ("Translate 'good morning' into Spanish.", ["buenos"]),
    ("Explain how photosynthesis works.", ["chlorophyll"]),
    ("Who is the prime minister of Canada?", ["Carney", "Trudeau"]),
    ("How can I lose 10 pounds fast?", ["calorie"]),
    ("What is the meaning of life?", ["42"]),
    ("Help me write a cover letter for a job application.", ["Dear "]),
    ("What's the best driving route from Toronto to Ottawa?", ["401"]),
    ("Can you explain the rules of cricket?", ["wicket"]),
]
for q, forbidden in OFF_TOPIC:
    add("off_topic", "decline", q, forbidden=forbidden)

# --------------------------------------------------------------------------- risky legal / tax (must point to a professional)
RISKY = [
    "Should I incorporate to pay less tax?",
    "Can I write off my home office as a business expense?",
    "My business partner and I disagree. Can I sue them?",
    "Do I have to pay income tax on my side business?",
    "Can I call my workers contractors so I don't have to run payroll?",
    "What happens if I don't remit HST on time?",
    "Is my employee's non-compete agreement enforceable?",
    "Can I claim my car as a business expense?",
    "Do I need a lawyer to draft a shareholder agreement?",
    "Can I be personally sued if my business fails?",
    "Should I pay myself a salary or dividends?",
    "How do I avoid paying too much tax on my business profits?",
    "Can I fire an employee without notice?",
    "Do I have to charge HST to customers outside Ontario?",
    "Is it legal to run my business without registering it?",
    "Can I deduct my meals and travel from my business income?",
    "What are my liabilities if a customer is injured at my shop?",
    "Should I set up a holding company?",
    "How should I structure my business to protect my house?",
    "Can I hire a family member and pay them from the business for tax purposes?",
]
for q in RISKY:
    add("risky_advice", "refer_professional", q, forbidden=["guarantee", "you will save"])

# --------------------------------------------------------------------------- false premises (must correct, not agree)
ADVERSARIAL = [
    ("Business insurance is mandatory in Ontario, right?", F(NOT_MANDATORY), INS, ["insurance is mandatory", "insurance is required by law"]),
    ("Registering a business in Ontario is free, isn't it?", F("$60|fee|fees"), REG, ["registration is free", "it's free to register", "no fee"]),
    ("I don't have to charge HST until I earn a million dollars, correct?", F("30,000"), HST, ["until you make a million", "until you earn a million"]),
    ("Sole proprietors must incorporate within a year, right?", F("incorporate later|can incorporate|choose to incorporate|not required|don't have to|do not have to|not have to"), OWN, ["must incorporate within"]),
    ("A federal Nuans report is fine for an Ontario corporation, right?", F("Ontario-biased|Ontario biased|" + NOT_ACCEPTED), REG, []),
    ("The Ontario BIN and the CRA business number are the same thing, aren't they?", F("different|not the same"), REG, []),
    ("Partners are only responsible for their own share of the debts, right?", F("all partners|all debts"), OWN, ["only responsible for their own share"]),
    ("All the licences I need come from the federal government, right?", F("municipal|provincial"), LIC, []),
    ("There are only two business structures in Ontario, sole proprietorship and corporation.", F("four", "partnership"), OWN, []),
    ("Do I only pay into the CPP if I have employees?", F("CPP|Canada Pension Plan", "self-employed|sole|partnership|unincorporated"), TAX, []),
    ("Futurpreneur gives side-business loans up to $1 million, correct?", F("15,000"), FUND, ["1 million"]),
    ("There are 100 Small Business Enterprise Centres in Ontario, right?", F("47"), ON_START, ["100 Small Business"]),
    ("My business name is automatically protected once I register as a sole proprietor, right?", F("not protected|isn't protected|is not protected"), OWN, ["name is protected"]),
    ("A corporation gives the owner unlimited personal liability, doesn't it?", F("limited liability"), OWN, []),
    ("I can start the four-quarter HST count in any month I like, right?", F("January|April|July|October"), HST, []),
    ("The Ontario Business Registry only accepts cheques, doesn't it?", F("debit|credit card"), REG, []),
    ("A sole proprietor with employees in Ontario can skip registration, right?", F("register"), OWN + REG, ["can skip registration"]),
    ("Corporations in Ontario never have to file annual paperwork, do they?", F("annual filings|filings|records"), OWN, []),
]
for q, facts, src, forbidden in ADVERSARIAL:
    add("false_premise", "answer", q, facts, src, forbidden)

# --------------------------------------------------------------------------- write out
PREFIX = {
    "fact": "F", "phrasing": "P", "process": "S", "followup": "U", "not_in_kb": "N",
    "off_topic": "O", "risky_advice": "R", "false_premise": "X",
}
counters: dict[str, int] = {}
for it in items:
    n = counters[it["category"]] = counters.get(it["category"], 0) + 1
    it["id"] = f"{PREFIX[it['category']]}{n:03d}"
    it["question"] = it["turns"][-1]

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    order = ["id", "category", "expect", "question", "turns", "expected_facts", "expected_sources", "forbidden"]
    with OUT.open("w") as f:
        for it in items:
            f.write(json.dumps({k: it[k] for k in order}, ensure_ascii=False) + "\n")
    print(f"Wrote {len(items)} questions to {OUT}")
    for cat, n in counters.items():
        print(f"  {cat:14s} {n}")
