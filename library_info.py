"""UOS Library AI - library_info.py

Verified OFFICIAL public information about the Wazir Agha Library,
University of Sargodha, taken from the university's own public pages
(research completed 21 November 2026). Every fact carries its source
URL so answers can attribute it.

This module is deliberately separate from:
  * the DEMO book catalogue (database.py / library.db - 80 sample books), and
  * the DEMO policy examples (kept in app.py, shown only on explicit request
    and always with the DEMO ONLY label).

Rules for this data:
  * Only facts published on official UOS pages are included here.
  * Anything NOT published (borrowing limits, loan periods, fines, fees,
    membership process, break timings, holiday closures) is NOT here -
    app.py answers those honestly with policy_not_published().
  * No Chief Librarian is named: the official pages conflict on that post.
    Dr Ghulam Mustafa is named ONLY in his published role as Turnitin
    focal person / Deputy Chief Librarian.
  * The internal research-repository address is never published here.
  * PakCat is a LINK-ONLY resource: no catalogue records are copied here.
"""

# ---------- Official sources ----------
SRC_LIBRARY_HOME = "https://library.su.edu.pk/"
SRC_LIBRARY_MAIN_UOS = "https://www.su.edu.pk/wazir_agha_library"
SRC_LIBRARY_ABOUT = "https://library.su.edu.pk/about"
SRC_LIBRARY_INFO = "https://library.su.edu.pk/information"
SRC_LIBRARY_SPACES = "https://library.su.edu.pk/libraryspaces"
SRC_EBOOKS = "https://ebooks.su.edu.pk/"
SRC_HEC = "https://www.digitallibrary.edu.pk/sargodhauni.html"
SRC_PAKCAT = "https://pakcat.pastic.gov.pk/library/45/university-of-sargodha"

LIBRARY_PHONE = "048-9230587"
LIBRARY_EMAIL = "library@uos.edu.pk"
LIBRARY_ADDRESS = "University Road, Sargodha, Punjab 40100, Pakistan"
CONTACT_LINE = f"{LIBRARY_EMAIL} | {LIBRARY_PHONE}"

# Exact label required on every demo-policy answer (decision D1).
DEMO_LABEL = (
    "DEMO ONLY — This is a sample rule for the student project, "
    "NOT an official University of Sargodha policy."
)


def _fact(en, ur, source):
    return {"en": en, "ur": ur, "source": source}


FACTS = {
    "hours": _fact(
        "📚 Wazir Agha Library opening hours:\n"
        "Monday to Friday: 8:00 AM – 8:00 PM\n"
        "Saturday: 9:00 AM – 5:00 PM\n"
        "Sunday hours are not listed on the library website — please contact "
        f"the library to confirm: {CONTACT_LINE}",
        "📚 Wazir Agha Library ki timings:\n"
        "Monday to Friday: 8:00 AM – 8:00 PM\n"
        "Saturday: 9:00 AM – 5:00 PM\n"
        "Sunday ki timing library ki website par darj nahi hai — confirm karne "
        f"ke liye library se rabta karein: {CONTACT_LINE}",
        SRC_LIBRARY_HOME,
    ),
    "sunday": _fact(
        "Sunday hours are not listed on the official Wazir Agha Library "
        "website, so I cannot confirm whether the library is open on Sunday. "
        f"Please confirm with the library: {CONTACT_LINE}",
        "Sunday ki timing official library website par darj nahi hai, is liye "
        "main confirm nahi kar sakta ke library Sunday ko khulti hai ya nahi. "
        f"Meherbani karke library se confirm karein: {CONTACT_LINE}",
        SRC_LIBRARY_HOME,
    ),
    "break": _fact(
        "Break / lunch timings are not published on the official library "
        "pages checked, so I cannot confirm a break time. The library's "
        f"published opening hours are 8:00 AM – 8:00 PM (Mon–Fri). Questions: {CONTACT_LINE}",
        "Break / lunch ki timing official library pages par publish nahi hai, "
        "is liye main koi break time confirm nahi kar sakta. Library ki "
        "published timing 8:00 AM – 8:00 PM (Mon–Fri) hai. "
        f"Sawal ke liye: {CONTACT_LINE}",
        SRC_LIBRARY_HOME,
    ),
    "contact": _fact(
        "📞 Wazir Agha Library, University of Sargodha\n"
        f"Phone: {LIBRARY_PHONE}\n"
        f"Email: {LIBRARY_EMAIL}\n"
        f"Address: {LIBRARY_ADDRESS}",
        "📞 Wazir Agha Library, University of Sargodha\n"
        f"Phone: {LIBRARY_PHONE}\n"
        f"Email: {LIBRARY_EMAIL}\n"
        f"Address: {LIBRARY_ADDRESS}",
        SRC_LIBRARY_HOME,
    ),
    "collections": _fact(
        "According to the main University of Sargodha page, Wazir Agha "
        "Library has 100,900 printed books, and around 75,000 electronic "
        "items are available through the HEC Digital Library Programme.\n"
        "Note: this chatbot's own searchable catalogue is a separate set of "
        "80 demonstration books — it is not the library's real collection.",
        "University of Sargodha ke main page ke mutabiq Wazir Agha Library "
        "mein 100,900 printed books hain, aur HEC Digital Library Programme "
        "ke zariye taqreeban 75,000 electronic items dastiyab hain.\n"
        "Note: is chatbot ki apni searchable catalogue alag 80 demo kitabon "
        "par hai — yeh library ki asal collection nahi hai.",
        SRC_LIBRARY_MAIN_UOS,
    ),
    "facilities": _fact(
        "🏛️ Wazir Agha Library facilities (library website): Learning "
        "Zone, Faculty Lounge, Research Commons, Digital Commons, "
        "Reference Hall, and discussion rooms (the library's spaces page "
        "lists eight discussion rooms) with LED screens for group work. "
        "Wi-Fi is available on all floors.",
        "🏛️ Wazir Agha Library ki sahulatain (library website ke mutabiq): "
        "Learning Zone, Faculty Lounge, Research Commons, Digital Commons, "
        "Reference Hall, aur discussion rooms (library ke spaces page par "
        "aath discussion rooms darj hain) jin mein group work ke liye LED "
        "screens hain. Wi-Fi tamam floors par dastiyab hai.",
        SRC_LIBRARY_SPACES,
    ),
    # The 700-user capacity is stated on the official About page - a
    # different source from the spaces list above, so it is kept as its
    # own fact and appended to facilities answers by get_fact().
    "capacity": _fact(
        "The library's official About page states a total seating "
        "capacity of 700 users at a time.",
        "Library ki official About page ke mutabiq library mein aik waqt "
        "mein 700 users ke baithne ki gunjaish hai.",
        SRC_LIBRARY_ABOUT,
    ),
    "seminar_libraries": _fact(
        "The library system includes five seminar libraries: Agriculture, "
        "Law, Pharmacy, Engineering & Technology, and Information Management.",
        "Library system mein paanch seminar libraries hain: Agriculture, "
        "Law, Pharmacy, Engineering & Technology, aur Information Management.",
        SRC_LIBRARY_ABOUT,
    ),
    "history": _fact(
        "Wazir Agha Library began as the Government College Sargodha library "
        "(Jinnah Block), became the university's Central Library in 2002, and "
        "moved to its purpose-built four-storey building in 2007. It was "
        "named after Wazir Agha in 2019 and renovated in 2023. It also holds "
        "the Government College Sargodha Archive Center.",
        "Wazir Agha Library ki ibtida Government College Sargodha ki library "
        "(Jinnah Block) se hui, 2002 mein yeh university ki Central Library "
        "bani, aur 2007 mein apni chaar-manzila makhsoos building mein shift "
        "hui. 2019 mein isay Wazir Agha ke naam se mansoob kiya gaya aur 2023 "
        "mein is ki tazween-o-araish hui. Yahan Government College Sargodha "
        "Archive Center bhi hai.",
        SRC_LIBRARY_ABOUT,
    ),
    "services": _fact(
        "Wazir Agha Library services include: reference support, a "
        "circulation desk for borrowing and returning, library orientation, "
        "information-literacy training (including EndNote, Mendeley and "
        "SPSS), literature-search and research support, Wi-Fi on all floors, "
        "document delivery, inter-library loan, and book-searching "
        "assistance — ask at the circulation desk and the item is held there "
        f"for pickup within 2 days. For research help, email {LIBRARY_EMAIL}.",
        "Wazir Agha Library ki services mein shamil hain: reference support, "
        "borrowing aur returning ke liye circulation desk, library "
        "orientation, information-literacy training (EndNote, Mendeley aur "
        "SPSS samait), literature-search aur research support, tamam floors "
        "par Wi-Fi, document delivery, inter-library loan, aur book-searching "
        "assistance — circulation desk par poochein, kitab wahan 2 din ke "
        f"andar pickup ke liye rakhi jati hai. Research madad ke liye email karein: {LIBRARY_EMAIL}.",
        SRC_LIBRARY_INFO,
    ),
    "wifi": _fact(
        "Wi-Fi is available on all floors of Wazir Agha Library. Login "
        "instructions are not published on the library pages checked — "
        f"please ask at the information desk or contact {CONTACT_LINE}.",
        "Wazir Agha Library ki tamam floors par Wi-Fi dastiyab hai. Login ka "
        "tareeqa library pages par publish nahi hai — information desk se "
        f"poochein ya rabta karein: {CONTACT_LINE}.",
        SRC_LIBRARY_INFO,
    ),
    "photocopy": _fact(
        "Photocopying and printing are available at the library (2nd floor, "
        "short range). Prices are not published on the library pages checked "
        f"— please ask at the library or contact {CONTACT_LINE}.",
        "Library mein photocopying aur printing ki sahulat hai (2nd floor, "
        "short range). Prices library pages par publish nahi hain — library "
        f"se poochein ya rabta karein: {CONTACT_LINE}.",
        SRC_LIBRARY_MAIN_UOS,
    ),
    "renewal": _fact(
        "According to the library's information page, students can renew and "
        "reserve books through the library portal using their account login, "
        "and can track their circulation there. The renewal conditions "
        "(periods and limits) are not published on the pages checked — for "
        f"details contact {CONTACT_LINE}.",
        "Library ki information page ke mutabiq students library portal par "
        "apne account login se kitabein renew aur reserve kar sakte hain, aur "
        "wahan apni circulation track kar sakte hain. Renewal ki conditions "
        "(period aur limits) pages par publish nahi hain — tafseel ke liye "
        f"rabta karein: {CONTACT_LINE}.",
        SRC_LIBRARY_INFO,
    ),
    "circulation": _fact(
        "Borrowing and returning are handled at the circulation desk "
        "(1st floor), which also handles library clearance. The library's "
        "published borrowing limits and loan periods are not given on the "
        f"public pages checked — please ask at the desk or contact {CONTACT_LINE}.",
        "Kitabein lena aur wapas karna circulation desk (1st floor) se hota "
        "hai, jahan library clearance bhi hota hai. Borrowing limits aur loan "
        "periods public pages par publish nahi hain — desk se poochein ya "
        f"rabta karein: {CONTACT_LINE}.",
        SRC_LIBRARY_INFO,
    ),
    "turnitin": _fact(
        "Similarity checking (Turnitin): MS/MPhil/PhD students need a "
        "similarity clearance certificate before submitting their thesis. "
        "Apply on the prescribed form through the proper channel. The focal "
        "person published on the library's information page is Dr Ghulam "
        "Mustafa, Deputy Chief Librarian — ghulam.mustafa@uos.edu.pk.",
        "Similarity checking (Turnitin): MS/MPhil/PhD students ko thesis "
        "submit karne se pehle similarity clearance certificate lazmi hai. "
        "Prescribed form par proper channel se apply karein. Library ki "
        "information page par published focal person Dr Ghulam Mustafa, "
        "Deputy Chief Librarian hain — ghulam.mustafa@uos.edu.pk.",
        SRC_LIBRARY_INFO,
    ),
    "ebooks": _fact(
        "The UOS e-books portal lets you search e-books by title, author or "
        f"ISBN: {SRC_EBOOKS}",
        "UOS e-books portal par aap title, author ya ISBN se e-books search "
        f"kar sakte hain: {SRC_EBOOKS}",
        SRC_EBOOKS,
    ),
    "hec": _fact(
        "The HEC Digital Library gives access to e-journals, e-books and "
        "databases (the library site names IEEE Xplore and Emerald Insight "
        "as examples). UOS access page: "
        f"{SRC_HEC}\n"
        "Off-campus access steps are not published on the library pages "
        f"checked — for help contact {CONTACT_LINE}.",
        "HEC Digital Library se e-journals, e-books aur databases tak rasai "
        "milti hai (library site par IEEE Xplore aur Emerald Insight ki "
        f"misal di gayi hai). UOS access page: {SRC_HEC}\n"
        "Off-campus access ke steps library pages par publish nahi hain — "
        f"madad ke liye rabta karein: {CONTACT_LINE}.",
        SRC_HEC,
    ),
    "catalogue": _fact(
        "The library's book catalogue is listed on PakCat (PASTIC's union "
        f"catalogue): {SRC_PAKCAT}\n"
        "How to use it: open the link and search by title, author, keyword, "
        "ISBN/ISSN, publisher or subject. A catalogue record shows that the "
        "library has catalogued the book — it does NOT confirm that a copy "
        "is available for borrowing right now; please confirm availability "
        "with the library. (The library website also links its own Koha "
        "catalogue, which was unreachable when checked on 21 November 2026.)\n"
        "This chatbot's own book search uses a separate 80-book "
        "demonstration catalogue only.",
        "Library ki books catalogue PakCat (PASTIC ki union catalogue) par "
        f"darj hai: {SRC_PAKCAT}\n"
        "Istemal ka tareeqa: link kholein aur title, author, keyword, "
        "ISBN/ISSN, publisher ya subject se search karein. Catalogue record "
        "ka matlab hai ke kitab library mein catalogued hai — is se yeh "
        "confirm NAHI hota ke copy is waqt borrowing ke liye available hai; "
        "availability library se confirm karein. (Library website apni Koha "
        "catalogue ka link bhi deti hai, jo 21 November 2026 ko check karne "
        "par unreachable tha.)\n"
        "Is chatbot ki apni book search sirf alag 80-book demonstration "
        "catalogue istemal karti hai.",
        SRC_PAKCAT,
    ),
}


def get_fact(key, roman_urdu=False):
    """Official fact text with its source link appended (both languages
    keep the original English source link - decision D3).

    Facilities answers also include the seating-capacity fact, because
    the two facts come from different official pages and each must show
    its own correct source (spaces page vs About page)."""
    fact = FACTS[key]
    text = fact["ur"] if roman_urdu else fact["en"]
    result = f"{text}\n\nSource: {fact['source']}"
    if key == "facilities":
        cap = FACTS["capacity"]
        cap_text = cap["ur"] if roman_urdu else cap["en"]
        result += f"\n\n{cap_text}\n\nSource: {cap['source']}"
    return result


def policy_not_published(topic_en, topic_ur, roman_urdu=False):
    """D1 default answer for real policy questions: honest 'not published'
    + official contact. NEVER includes demo figures or sample rules."""
    if roman_urdu:
        return (
            f"{topic_ur} official library pages par publish nahi hai jo check "
            "ki gayi hain, is liye main aap ko koi official figure nahi de "
            "sakta. Meherbani karke library se poochein: "
            f"{CONTACT_LINE}"
        )
    return (
        f"The official {topic_en} is not published in the library sources "
        "checked, so I cannot give you an official figure. Please ask the "
        f"library directly: {CONTACT_LINE}"
    )
