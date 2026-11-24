"""UOS Library AI - library_guides_faq.py

Stage 4.6: 6 Student Guidance & Procedural Knowledge guides
(G01-G06), added 24 November 2026. Each guide assembles ONLY facts
already verified in this project's official sources (the VC-approved
Code of Conduct, the library Information / Spaces / Research Support
pages, the main UOS library page - all read in full on 21-23
November 2026) into a complete step-by-step answer. Where a
procedure is NOT published in the sources checked, the guide says
so plainly ("not published in the sources checked") and directs the
student to the correct desk and the library contact instead of
inventing steps, documents, fees or eligibility.

Nothing here adds a new factual claim about the University of
Sargodha: G01-G03 are honest not-published guides (membership
process, lost-card replacement, complaints procedure), G04 is
general guidance built on the verified PakCat catalogue link, G05
restates the verified Research Support Lab facts as steps, and G06
combines the verified reservation procedure with the verified
electronic alternatives. This module is checked AFTER the other
four FAQ modules in app.py, so the specific module answers keep
priority and the guides only catch what falls through.
"""

from library_faq import _content_words, _normalize, _phrase_score

SRC_INFO = "https://library.su.edu.pk/information"
SRC_RSL = "https://library.su.edu.pk/supportlab"
SRC_PAKCAT = "https://pakcat.pastic.gov.pk/library/45/university-of-sargodha"
SRC_COC = ("https://www.scribd.com/document/767759639/"
           "Code-of-Conduct-Wazir-Agha-Library-UOS")

CONTACT_LINE = "library@uos.edu.pk · 048-9230587"

STATUS_VERIFIED = "officially verified"
STATUS_GUIDANCE = "general guidance"
STATUS_NOT_PUBLISHED = "not published"
STATUS_COC = "official_code_of_conduct"


def _faq(fid, category, q_en, q_ru, a_en, a_ru, source, status, match):
    return {
        "id": fid, "category": category, "q_en": q_en, "q_ru": q_ru,
        "a_en": a_en, "a_ru": a_ru, "source": source, "status": status,
        "match": match,
    }


FAQS = [
    _faq("G01", "Membership and access guides",
         "How do I become a member of the library?",
         "Main library ka member kaise ban sakta hun?",
         "**Direct answer:** The library's membership process — any form, documents or approval needed — is **not published in the sources checked**, so I cannot give you an official step list for it.\n\n**What you can do:**\n1. Take your **UOS student ID card** with you — displaying your ID card in the library is required, and it is the first thing the staff will ask about.\n2. Go to the **Circulation Desk (first floor)** of the Wazir Agha Library and ask the staff for the current membership process.\n3. Or ask before you visit: " + CONTACT_LINE + ".\n\n**Remember:** This chatbot cannot create a membership or register you — membership is done by the library itself. Anyone who is not yet a member can still ask questions here in guest mode.",
         "**Seedha jawab:** Library ki membership ka process — koi form, documents ya approval — **un sources mein published nahi hai jo check kiye gaye**, is liye main aap ko is ki official step list nahi de sakta.\n\n**Aap kya kar sakte hain:**\n1. Apna **UOS student ID card** sath le jayein — library mein ID card display karna lazmi hai, aur staff sab se pehle isi ke baare mein poochein ge.\n2. Wazir Agha Library ke **Circulation Desk (first floor)** par jayein aur staff se current membership process poochein.\n3. Ya jane se pehle pooch lein: " + CONTACT_LINE + ".\n\n**Yaad rakhein:** Yeh chatbot membership nahi bana sakta aur aap ko register nahi kar sakta — membership library khud karti hai. Jo abhi member nahi hai woh yahan guest mode mein sawalat pooch sakta hai.",
         SRC_INFO, STATUS_NOT_PUBLISHED,
         ["how do i become a member", "become a library member",
          "library membership kaise", "member banne ka tarika",
          "how to get library membership", "library member banna",
          "membership lene ka tarika", "join the library",
          "become a member of the library"]),
    _faq("G02", "Membership and access guides",
         "What should I do if I lose my UOS ID card or library card?",
         "Agar mera UOS ID card ya library card kho jaye to kya karun?",
         "**Direct answer:** A replacement process for a lost ID card or library card is **not published in the sources checked** — but act promptly, because displaying your ID card in the library is required.\n\n**Steps:**\n1. **Search once more** — check your bag, room and classroom first.\n2. **Report the loss promptly** at the **Circulation Desk (first floor)** so the library staff know your card is missing and can guide you about using the library meanwhile.\n3. **For a replacement university ID card**, ask your department office / the university administration — they issue student ID cards (general guidance).\n4. For library-side questions, contact the library: " + CONTACT_LINE + ".\n\n**Remember:** This chatbot cannot issue or replace cards.",
         "**Seedha jawab:** Khoye hue ID card ya library card ki replacement ka process **un sources mein published nahi hai jo check kiye gaye** — lekin foran action lein, kyunke library mein ID card display karna lazmi hai.\n\n**Steps:**\n1. **Aik dafa phir dhundein** — pehle apna bag, kamra aur classroom check kar lein.\n2. **Ghumshudgi ki report foran karein** **Circulation Desk (first floor)** par, taake library staff ko maloom ho ke aap ka card ghayab hai aur woh is doran library use karne ke baare mein rehnumai kar sakein.\n3. **Replacement university ID card ke liye** apne department office / university administration se poochein — student ID cards wohi issue karte hain (general guidance).\n4. Library se mutalliqa sawalon ke liye rabta karein: " + CONTACT_LINE + ".\n\n**Yaad rakhein:** Yeh chatbot cards issue ya replace nahi kar sakta.",
         SRC_INFO, STATUS_NOT_PUBLISHED,
         ["lost my id card", "lost my library card", "id card kho gaya",
          "library card lost", "card ghum gaya kya karun",
          "lost id card what to do", "mera card kho gaya",
          "id card lost ho gaya"]),
    _faq("G03", "Membership and access guides",
         "How do I make a complaint or give feedback about the library?",
         "Main library ke baare mein complaint ya feedback kaise dun?",
         "**Direct answer:** No formal complaints procedure is published in the sources checked — the library is contacted directly.\n\n**Steps:**\n1. Note down the details first: **what happened, when, and at which desk or section** — a specific complaint is easier to act on.\n2. **Email the library:** library@uos.edu.pk, or **phone:** 048-9230587.\n3. Or visit in person and ask at the **Information Desk / Circulation Desk (first floor)** to speak to the staff responsible.\n\n**Remember:** Be specific and polite — and keep a copy of your email. This chatbot cannot forward complaints for you.",
         "**Seedha jawab:** Koi formal complaints procedure un sources mein published nahi hai jo check kiye gaye — library se seedha rabta kiya jata hai.\n\n**Steps:**\n1. Pehle tafseel note kar lein: **kya hua, kab hua, aur kis desk ya section mein** — specific complaint par amal asan hota hai.\n2. **Library ko email karein:** library@uos.edu.pk, ya **phone karein:** 048-9230587.\n3. Ya khud ja kar **Information Desk / Circulation Desk (first floor)** par zimmedar staff se baat karne ko kahein.\n\n**Yaad rakhein:** Specific aur shistagi se likhein — aur apni email ki copy sambhal kar rakhein. Yeh chatbot aap ki complaint forward nahi kar sakta.",
         SRC_INFO, STATUS_NOT_PUBLISHED,
         ["make a complaint", "complaint about the library",
          "shikayat karni hai", "give feedback to the library",
          "library complaint kaise", "feedback dena hai",
          "complain about library", "complaint kaise karun"]),
    _faq("G04", "Book search and shelf guides",
         "How do I find a book on the library shelves?",
         "Main library ki shelves par kitab kaise dhundun?",
         "**Direct answer:** Find the book in the catalogue first, then go to the shelves — do not wander the shelves hoping to spot it (general guidance, built on the library's verified catalogue links).\n\n**Steps:**\n1. **Search the catalogue first.** The PakCat union catalogue lists this library's collection — search it by title or author: pakcat.pastic.gov.pk/library/45/university-of-sargodha.\n2. **Note the book's exact details** (title, author, edition) from the catalogue record before you go.\n3. **In this app**, the demo catalogue shows each demo book's **shelf location** in its record — but remember those 80 books are demonstration data, not the real shelves.\n4. **If you still cannot locate the book, ask the staff** at the Circulation Desk (first floor) — they can check whether it is issued, reserved or shelved elsewhere.\n\n**Remember:** If the book is issued to someone else, you can reserve it with the prescribed form at the Circulation Desk.",
         "**Seedha jawab:** Pehle kitab catalogue mein dhundein, phir shelves ki taraf jayein — shelves par idhar udhar ghoom kar kitab milne ki umeed na rakhein (general guidance, library ke verified catalogue links par mabni).\n\n**Steps:**\n1. **Pehle catalogue search karein.** PakCat union catalogue mein is library ki collection list hai — title ya author se search karein: pakcat.pastic.gov.pk/library/45/university-of-sargodha.\n2. **Kitab ki exact details note kar lein** (title, author, edition) catalogue record se, jane se pehle.\n3. **Is app mein**, demo catalogue har demo book ki **shelf location** us ke record mein dikhata hai — lekin yaad rakhein woh 80 books demonstration data hain, asal shelves nahi.\n4. **Agar phir bhi kitab na mile to staff se poochein** Circulation Desk (first floor) par — woh check kar sakte hain ke kitab issued hai, reserved hai ya kahin aur rakhi hai.\n\n**Yaad rakhein:** Agar kitab kisi aur ko issued ho to aap use Circulation Desk par prescribed form se reserve kar sakte hain.",
         SRC_PAKCAT, STATUS_GUIDANCE,
         ["find a book on the shelf", "book shelf par kahan",
          "shelf par kitab dhundna", "how to find a book in the library",
          "kitab shelf se dhundna", "locate a book on the shelves",
          "find book on shelves", "shelf se kitab"]),
    _faq("G05", "Research support guides",
         "How can the Research Support Lab help with my research?",
         "Research Support Lab meri research mein kaise madad kar sakta hai?",
         "**Direct answer:** The Research Support Lab (RSL) is the library's research-training service, housed in the **Digital Commons** of the Wazir Agha Library.\n\n**How it helps:**\n1. It runs **paid trainings** on published research topics — for example how to conduct systematic reviews and meta-analysis, literature review using NVivo or Qiqqa, research methodology, and tools such as SPSS and SmartPLS (25 topics are published on its page).\n2. **Visit the lab in the Digital Commons** and discuss your research stage and what you need.\n3. **Ask for Mr. Javed Iqbal**, Assistant Librarian (Research Support), or contact the lab through the library: " + CONTACT_LINE + ".\n4. **Confirm the fee and schedule before enrolling** — trainings are paid, but the fees are not published on the lab's page.\n\n**Remember:** The lab trains and guides you — it does not do your research or write your work for you, and this chatbot cannot enrol you.",
         "**Seedha jawab:** Research Support Lab (RSL) library ki research-training service hai, jo Wazir Agha Library ke **Digital Commons** mein waqe hai.\n\n**Yeh kaise madad karta hai:**\n1. Yeh published research topics par **paid trainings** deta hai — masalan systematic reviews aur meta-analysis kaise conduct karein, NVivo ya Qiqqa se literature review, research methodology, aur SPSS aur SmartPLS jaisay tools (is ke page par 25 topics published hain).\n2. **Digital Commons mein lab visit karein** aur apni research ki stage aur zaroorat discuss karein.\n3. **Mr. Javed Iqbal**, Assistant Librarian (Research Support), se milne ko kahein, ya library ke zariye rabta karein: " + CONTACT_LINE + ".\n4. **Enroll karne se pehle fee aur schedule confirm kar lein** — trainings paid hain, lekin fees lab ke page par published nahi hain.\n\n**Yaad rakhein:** Lab aap ko train aur guide karta hai — woh aap ki research nahi karta aur aap ka kaam nahi likhta, aur yeh chatbot aap ko enrol nahi kar sakta.",
         SRC_RSL, STATUS_VERIFIED,
         ["research support lab help", "rsl se madad",
          "research support lab kaise madad", "help with my research lab",
          "research mein lab ki madad", "support lab research help",
          "lab research help karega"]),
    _faq("G06", "Book search and shelf guides",
         "What should I do if the book I need is not available?",
         "Agar mujhe jo kitab chahiye woh available na ho to kya karun?",
         "**Direct answer:** It depends why it is unavailable — here is what to do in each case.\n\n**If the book is issued to someone else:**\n1. Submit the **prescribed reservation form** at the Circulation Desk (first floor).\n2. When it is returned, **collect it within two days** — a reservation request stands cancelled after two days.\n\n**If you cannot find it on the shelves:**\n3. Ask the staff at the Circulation Desk — it may be issued, reserved, or shelved elsewhere.\n\n**Check an electronic version:**\n4. Search the **UOS e-books portal** (ebooks.su.edu.pk) by title, author or ISBN, and the **HEC Digital Library** resources arranged for UOS.\n\n**In this app:** the catalogue holds 80 demo books only (demonstration data) — if a book is not there, the app will say so honestly and may suggest related demo books; that does not mean the real library lacks the book. For the real collection, ask the library: " + CONTACT_LINE + ".",
         "**Seedha jawab:** Yeh is par depend karta hai ke kitab kyun available nahi — har surat mein kya karna hai, yeh raha.\n\n**Agar kitab kisi aur ko issued hai:**\n1. Circulation Desk (first floor) par **prescribed reservation form** jama karwayein.\n2. Jab kitab wapas aaye to **do din ke andar le lein** — reservation request do din ke baad cancelled ho jati hai.\n\n**Agar shelves par na mile:**\n3. Circulation Desk par staff se poochein — ho sakta hai kitab issued ho, reserved ho, ya kahin aur rakhi ho.\n\n**Electronic version check karein:**\n4. **UOS e-books portal** (ebooks.su.edu.pk) par title, author ya ISBN se search karein, aur UOS ke liye arranged **HEC Digital Library** resources bhi dekhein.\n\n**Is app mein:** catalogue mein sirf 80 demo books hain (demonstration data) — agar koi kitab wahan nahi to app saaf bata dega aur related demo books suggest kar sakta hai; is ka matlab yeh nahi ke asal library mein woh kitab nahi hai. Asal collection ke liye library se poochein: " + CONTACT_LINE + ".",
         SRC_COC, STATUS_COC,
         ["book is not available", "book not available what to do",
          "kitab available nahi hai", "book unavailable options",
          "jo kitab chahiye woh nahi mili", "book not in library",
          "needed book not available", "book available nahi to"]),
]


# ---------------- Matching (same strict design as library_faq.py) ------
for _f in FAQS:
    _f["_q_words"] = (_content_words(_f["q_en"]), _content_words(_f["q_ru"]))


def find_guide_faq(text):
    """Return the single best-matching guide FAQ dict, or None."""
    norm = " " + _normalize(text) + " "
    user_words = set(_normalize(text).split())
    user_content = _content_words(text)
    best, best_score, second_score = None, 0, 0
    for faq in FAQS:
        score = 0
        for phrase in faq["match"]:
            p = _normalize(phrase)
            if (" " + p + " ") in norm or norm.strip() == p:
                score += _phrase_score(p)
        best_bonus = 0
        for q_words in faq["_q_words"]:
            if len(q_words) >= 3:
                q_digits = {w for w in q_words if w.isdigit()}
                if q_digits and not q_digits <= user_words:
                    continue
                matched = len(q_words & user_words)
                containment = matched / len(q_words)
                coverage = matched / len(user_content) if user_content else 0
                if containment >= 0.8 and coverage >= 0.45:
                    best_bonus = max(
                        best_bonus, 500 + matched * 20 + round(containment * 50))
        score += best_bonus
        if score > best_score:
            best, second_score, best_score = faq, best_score, score
        elif score > second_score:
            second_score = score
    if best is not None and best_score >= 20 and best_score > second_score:
        return best
    return None


# Roman Urdu hint words for answer-language detection (shared list).
from library_faq import _FAQ_URDU_WORDS


def guide_faq_answer(text, roman_urdu=False):
    """Full guide-FAQ answer (with source link), or None."""
    faq = find_guide_faq(text)
    if faq is None:
        return None
    if not roman_urdu:
        words = set(_normalize(text).split())
        roman_urdu = len(words & _FAQ_URDU_WORDS) >= 2
    body = faq["a_ru"] if roman_urdu else faq["a_en"]
    return f"{body}\n\nSource: {faq['source']}"
