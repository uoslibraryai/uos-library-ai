"""UOS Library AI - library_services_faq.py

60 Facilities & Services FAQs for the Wazir Agha Library, University
of Sargodha, built ONLY from official sources checked on 23 November
2026 (the Library Spaces and Research Support pages were read in
full; the Information Services page was read in full the same day):

  * SRC_SPACES - https://library.su.edu.pk/libraryspaces
  * SRC_INFO   - https://library.su.edu.pk/information
  * SRC_RSL    - https://library.su.edu.pk/supportlab
  * SRC_HOME   - https://library.su.edu.pk/
  * SRC_MAIN   - https://www.su.edu.pk/wazir_agha_library
  * SRC_EBOOKS - https://ebooks.su.edu.pk/
  * SRC_HEC    - https://www.digitallibrary.edu.pk/sargodhauni.html
  * SRC_COC    - the VC-approved Code of Conduct (floor layout in its
    table of contents), already used by library_faq.py.

Source status values (per entry): "officially verified",
"general guidance", or "not published".

Honesty rules kept from the rest of the project:
  * Discussion rooms: the current Library Spaces page lists 8 rooms
    (8 users each). An older official About page says 5 - the FAQs
    state 8 from the current Spaces page and explain the discrepancy.
  * Wi-Fi login credentials/procedure, photocopy charges, Research
    Support Lab fees, Turnitin thresholds/charges/turnaround are NOT
    published in the sources checked - the FAQs say so and give the
    library contact instead of inventing figures.
  * The chatbot cannot itself book rooms, print, issue books, run
    Turnitin checks or process inter-library loans; answers only
    explain the library's own services.

Matching uses the same strict two-channel matcher as library_faq.py
(distinctive phrases + 80% canonical-question containment with a
number-token guard; ties return None). This module is checked AFTER
the 100 Rules & Regulations FAQs in app.py, so rules answers keep
priority for rules questions.
"""

from library_faq import _content_words, _normalize, _phrase_score

SRC_SPACES = "https://library.su.edu.pk/libraryspaces"
SRC_INFO = "https://library.su.edu.pk/information"
SRC_RSL = "https://library.su.edu.pk/supportlab"
SRC_HOME = "https://library.su.edu.pk/"
SRC_MAIN = "https://www.su.edu.pk/wazir_agha_library"
SRC_COC = "https://www.scribd.com/document/767759639/Code-of-Conduct-Wazir-Agha-Library-UOS"

CONTACT_LINE = "library@uos.edu.pk | 048-9230587"

STATUS_VERIFIED = "officially verified"
STATUS_GUIDANCE = "general guidance"
STATUS_NOT_PUBLISHED = "not published"


def _faq(fid, category, q_en, q_ru, a_en, a_ru, source, status, match):
    return {
        "id": fid, "category": category, "q_en": q_en, "q_ru": q_ru,
        "a_en": a_en, "a_ru": a_ru, "source": source, "status": status,
        "match": match,
    }


FAQS = [
    # ============ Category 1: Reading areas and library spaces (10) ======
    _faq("FS01", "Reading areas and library spaces",
         "Where can I study in the library?",
         "Main library mein kahan parh sakta hun?",
         "You can study in the Learning Zone (ground floor), the Reference Hall, the Digital Commons, and — for group work — the discussion rooms. Graduate students (MPhil/PhD) can also use the Research Commons. The Faculty Lounge is reserved for faculty.",
         "Aap Learning Zone (ground floor), Reference Hall, Digital Commons mein parh sakte hain, aur group work ke liye discussion rooms use kar sakte hain. Graduate students (MPhil/PhD) Research Commons bhi use kar sakte hain. Faculty Lounge sirf faculty ke liye hai.",
         SRC_SPACES, STATUS_VERIFIED,
         ["where can i study", "where to study in library", "kahan parh sakta",
          "study in the library where", "parhne ki jagah"]),
    _faq("FS02", "Reading areas and library spaces",
         "How many students can sit in the Learning Zone?",
         "Learning Zone mein kitne students baith sakte hain?",
         "The Learning Zone has a sitting capacity of 150 users, with flexible seating such as carrels, sofas, high chairs, tables and reading chairs.",
         "Learning Zone mein 150 users ke baithne ki capacity hai, jahan carrels, sofas, high chairs, tables aur reading chairs jaisi flexible seating hai.",
         SRC_SPACES, STATUS_VERIFIED,
         ["learning zone capacity", "sit in the learning zone", "learning zone mein kitne",
          "learning zone seats", "how many students learning zone"]),
    _faq("FS03", "Reading areas and library spaces",
         "What kind of seating is in the Learning Zone?",
         "Learning Zone mein kis qisam ki seating hai?",
         "The Learning Zone offers flexible seating: carrels, sofas, high chairs, tables, and reading chairs with tables — you can choose what suits your study style.",
         "Learning Zone mein flexible seating hai: carrels, sofas, high chairs, tables, aur reading chairs with tables — aap apne study style ke mutabiq chun sakte hain.",
         SRC_SPACES, STATUS_VERIFIED,
         ["seating is in the learning zone", "kind of seating learning", "learning zone seating",
          "learning zone mein seating"]),
    _faq("FS04", "Reading areas and library spaces",
         "How many people can use the Faculty Lounge?",
         "Faculty Lounge kitne log use kar sakte hain?",
         "The Faculty Lounge is a designated place for university faculty with a capacity of 60 users, where faculty can use various library facilities. It is not for students.",
         "Faculty Lounge university faculty ke liye makhsoos jagah hai jis ki capacity 60 users hai, jahan faculty mukhtalif library facilities use kar sakte hain. Yeh students ke liye nahi hai.",
         SRC_SPACES, STATUS_VERIFIED,
         ["faculty lounge capacity", "how many people faculty lounge", "faculty lounge kitne",
          "faculty lounge users"]),
    _faq("FS05", "Reading areas and library spaces",
         "What is the capacity of the Research Commons?",
         "Research Commons ki capacity kitni hai?",
         "The Research Commons has 75 sitting places. It is designated for research students (MPhil/PhD), has a large LED screen, can be turned into a seminar room when needed, and includes two discussion rooms.",
         "Research Commons mein 75 sitting places hain. Yeh research students (MPhil/PhD) ke liye makhsoos hai, is mein large LED screen hai, zaroorat parne par yeh seminar room mein badal sakta hai, aur is mein do discussion rooms bhi hain.",
         SRC_SPACES, STATUS_VERIFIED,
         ["capacity of the research commons", "research commons capacity", "research commons ki capacity",
          "research commons seats"]),
    _faq("FS06", "Reading areas and library spaces",
         "How many users can use the Digital Commons at one time?",
         "Digital Commons aik waqt mein kitne users use kar sakte hain?",
         "The Digital Commons has a sitting capacity of 40 users, with a large LED screen and the latest computer systems. It can be used by all library users.",
         "Digital Commons mein 40 users ke baithne ki capacity hai, jahan large LED screen aur latest computer systems hain. Yeh tamam library users use kar sakte hain.",
         SRC_SPACES, STATUS_VERIFIED,
         ["digital commons at one time", "digital commons capacity", "digital commons kitne users",
          "how many users digital commons"]),
    _faq("FS07", "Reading areas and library spaces",
         "How many seats are there in the Reference Hall?",
         "Reference Hall mein kitni seats hain?",
         "The Reference Hall has a capacity of about 100 users. Reference books are placed in this hall, the reference librarian's office is also there, and the hall includes two discussion rooms.",
         "Reference Hall ki capacity taqreeban 100 users hai. Is hall mein reference books rakhi hain, reference librarian ka office bhi yahin hai, aur hall mein do discussion rooms bhi hain.",
         SRC_SPACES, STATUS_VERIFIED,
         ["seats in the reference hall", "reference hall seats", "reference hall capacity",
          "reference hall mein kitni seats"]),
    _faq("FS08", "Reading areas and library spaces",
         "What is the total seating capacity of the library?",
         "Library ki total seating capacity kitni hai?",
         "The library's official About page states a total seating capacity of 700 users at a time.",
         "Library ki official About page ke mutabiq library mein aik waqt mein total 700 users ke baithne ki capacity hai.",
         "https://library.su.edu.pk/about", STATUS_VERIFIED,
         ["total seating capacity", "total capacity of the library", "library ki total capacity",
          "how many users can sit in the library"]),
    _faq("FS09", "Reading areas and library spaces",
         "Are there study carrels in the library?",
         "Kya library mein study carrels hain?",
         "Yes. The Learning Zone seating includes carrels, and the Research Commons has study carrels for individual researchers. Under the Code of Conduct, a study carrel is for a single user only.",
         "Ji haan. Learning Zone ki seating mein carrels shamil hain, aur Research Commons mein individual researchers ke liye study carrels hain. Code of Conduct ke mutabiq study carrel sirf aik user ke liye hota hai.",
         SRC_SPACES, STATUS_VERIFIED,
         ["study carrels in the library", "are there study carrels", "study carrels hain",
          "carrels available"]),
    _faq("FS10", "Reading areas and library spaces",
         "Which facilities are on which floor of the library?",
         "Library ki kis floor par kya facilities hain?",
         "Ground floor: Information Desk, Learning Zone and Faculty Lounge. First floor: Circulation Desk, Reference Hall, discussion rooms, Research Commons and Digital Commons. The book collections are on the 2nd and 3rd floors, and photocopying is on the 2nd floor.",
         "Ground floor: Information Desk, Learning Zone aur Faculty Lounge. First floor: Circulation Desk, Reference Hall, discussion rooms, Research Commons aur Digital Commons. Book collections 2nd aur 3rd floors par hain, aur photocopying 2nd floor par hai.",
         SRC_COC, STATUS_VERIFIED,
         ["which floor", "kis floor par kya", "facilities on which floor", "floor wise facilities",
          "which facilities are on"]),

    # ============ Category 2: Discussion rooms and facilities (8) ========
    _faq("FS11", "Discussion rooms and facilities",
         "How many discussion rooms are there in the library?",
         "Library mein kitne discussion rooms hain?",
         "The library's current Library Spaces page lists eight (8) discussion rooms. Note: an older official About page mentions five — the Spaces page is the current one, and it lists 8, each for 8 users with a 42-inch LED screen.",
         "Library ki current Library Spaces page par aath (8) discussion rooms darj hain. Note: aik purani official About page par paanch (5) ka zikr hai — Spaces page current hai, aur us par 8 darj hain, har aik 8 users ke liye 42-inch LED screen ke sath.",
         SRC_SPACES, STATUS_VERIFIED,
         ["how many discussion rooms", "kitne discussion rooms", "number of discussion rooms",
          "total discussion rooms"]),
    _faq("FS12", "Discussion rooms and facilities",
         "How many people can use one discussion room?",
         "Aik discussion room kitne log use kar sakte hain?",
         "Each discussion room has a capacity of 8 users.",
         "Har discussion room ki capacity 8 users hai.",
         SRC_SPACES, STATUS_VERIFIED,
         ["one discussion room", "people can use one discussion", "discussion room kitne log",
          "capacity of one discussion room", "how many people in a discussion room"]),
    _faq("FS13", "Discussion rooms and facilities",
         "Do the discussion rooms have screens for presentations?",
         "Kya discussion rooms mein presentations ke liye screens hain?",
         "Yes. Each discussion room is equipped with a 42-inch LED screen having Wi-Fi and Bluetooth connectivity, for group presentations and learning.",
         "Ji haan. Har discussion room mein 42-inch LED screen hai jis mein Wi-Fi aur Bluetooth connectivity hai, group presentations aur learning ke liye.",
         SRC_SPACES, STATUS_VERIFIED,
         ["discussion rooms have screens", "screens for presentations", "discussion room led",
          "discussion rooms mein screens"]),
    _faq("FS14", "Discussion rooms and facilities",
         "Can we give a group presentation in a discussion room?",
         "Kya hum discussion room mein group presentation de sakte hain?",
         "Yes — the discussion rooms are made for that: each has a 42-inch LED screen with Wi-Fi and Bluetooth connectivity for group presentations and learning. If you need the LED switched on or off, request the library staff (multimedia service).",
         "Ji haan — discussion rooms isi liye hain: har aik mein 42-inch LED screen Wi-Fi aur Bluetooth connectivity ke sath hai, group presentations aur learning ke liye. Agar LED on ya off karwana ho to library staff se request karein (multimedia service).",
         SRC_SPACES, STATUS_VERIFIED,
         ["group presentation in a discussion room", "give a group presentation",
          "group presentation de sakte", "presentation in discussion room"]),
    _faq("FS15", "Discussion rooms and facilities",
         "Where are the discussion rooms located?",
         "Discussion rooms kahan waqe hain?",
         "The discussion rooms are on the first floor area of the library — the Reference Hall includes two discussion rooms and the Research Commons also has two, with eight discussion rooms in total across the library.",
         "Discussion rooms library ke first floor area mein hain — Reference Hall mein do discussion rooms hain aur Research Commons mein bhi do, aur library bhar mein total aath discussion rooms hain.",
         SRC_SPACES, STATUS_VERIFIED,
         ["discussion rooms located", "where are the discussion rooms", "discussion rooms kahan",
          "discussion rooms where"]),
    _faq("FS16", "Discussion rooms and facilities",
         "Can you check if a discussion room is free right now?",
         "Kya aap check kar sakte hain ke abhi discussion room free hai?",
         "I cannot check live room availability — this chatbot has no access to the library's booking records. Room allocation is subject to availability; please ask at the Circulation Desk (first floor) for the current position.",
         "Main live room availability check nahi kar sakta — is chatbot ko library ke booking records tak rasai nahi hai. Room allocation availability ke tehat hoti hai; maujooda position ke liye Circulation Desk (first floor) se poochein.",
         SRC_SPACES, STATUS_GUIDANCE,
         ["room is free right now", "check if a discussion room is free", "discussion room free hai",
          "room available right now", "check room availability"]),
    _faq("FS17", "Discussion rooms and facilities",
         "Can you book a discussion room for me?",
         "Kya aap mere liye discussion room book kar sakte hain?",
         "No — I cannot book rooms. To reserve a discussion room, complete the reservation form and submit it at the Circulation Desk (first floor), at least one hour in advance; rooms are allocated first-come, first-served, subject to availability.",
         "Nahi — main rooms book nahi kar sakta. Discussion room reserve karne ke liye reservation form mukammal karke Circulation Desk (first floor) par jama karayein, kam az kam aik ghanta pehle; rooms first-come, first-served milte hain, availability ke tehat.",
         SRC_SPACES, STATUS_GUIDANCE,
         ["book a room for me", "book a discussion room for me", "mere liye room book",
          "can you book a room", "book room for me"]),
    _faq("FS18", "Discussion rooms and facilities",
         "Can I connect my laptop to the discussion room LED screen?",
         "Kya main apna laptop discussion room ki LED screen se connect kar sakta hun?",
         "Yes. The 42-inch LED screens in the discussion rooms have Wi-Fi and Bluetooth connectivity, so you can connect your device for group presentations and learning.",
         "Ji haan. Discussion rooms ki 42-inch LED screens mein Wi-Fi aur Bluetooth connectivity hai, is liye aap apna device group presentations aur learning ke liye connect kar sakte hain.",
         SRC_SPACES, STATUS_VERIFIED,
         ["connect my laptop to the discussion", "laptop connect led", "connect to the led screen",
          "laptop led se connect"]),

    # ============ Category 3: Reference and information services (8) =====
    _faq("FS19", "Reference and information services",
         "Where is the Reference Hall?",
         "Reference Hall kahan hai?",
         "The Reference Hall is on the first floor of the library. It holds the reference books, seats about 100 users, includes two discussion rooms, and the reference librarian's office is situated in this hall.",
         "Reference Hall library ke first floor par hai. Is mein reference books hain, taqreeban 100 users ki seats hain, do discussion rooms hain, aur reference librarian ka office bhi isi hall mein hai.",
         SRC_SPACES, STATUS_VERIFIED,
         ["where is the reference hall", "reference hall kahan hai", "reference hall location",
          "reference hall where"]),
    _faq("FS20", "Reference and information services",
         "What help can I get at the Information Desk?",
         "Information Desk se mujhe kya madad mil sakti hai?",
         "Information Desks provide in-depth reference and information support for your queries. There are two: the ground floor desk serves during the library's opening hours on all working days, and the second floor desk serves from 8:00 AM to 5:00 PM.",
         "Information Desks aap ke sawalat ke liye in-depth reference aur information support faraham karte hain. Do desks hain: ground floor desk tamam working days mein library ke opening hours ke doran serve karta hai, aur second floor desk 8:00 AM se 5:00 PM tak serve karta hai.",
         SRC_INFO, STATUS_VERIFIED,
         ["help at the information desk", "information desk help", "information desk se madad",
          "what help information desk"]),
    _faq("FS21", "Reference and information services",
         "Can I ask the library a question by email?",
         "Kya main library ko email par sawal pooch sakta hun?",
         f"Yes. Users may make queries by email at {CONTACT_LINE.split(' | ')[0]}. You can also call the library at {CONTACT_LINE.split(' | ')[1]}.",
         f"Ji haan. Users email par queries kar sakte hain: {CONTACT_LINE.split(' | ')[0]}. Aap library ko call bhi kar sakte hain: {CONTACT_LINE.split(' | ')[1]}.",
         SRC_INFO, STATUS_VERIFIED,
         ["ask by email", "question by email", "email par sawal", "library ko email",
          "email the library"]),
    _faq("FS22", "Reference and information services",
         "Does the library offer orientation for new students?",
         "Kya library new students ke liye orientation deti hai?",
         "Yes. The library's information-literacy programmes include orientation sessions for users, along with hands-on trainings, in-class sessions, workshops and seminars. To request a session, email the library: library@uos.edu.pk.",
         "Ji haan. Library ke information-literacy programmes mein users ke liye orientation sessions shamil hain, is ke ilawa hands-on trainings, in-class sessions, workshops aur seminars bhi hain. Session request karne ke liye library ko email karein: library@uos.edu.pk.",
         SRC_INFO, STATUS_VERIFIED,
         ["orientation for new students", "library orientation", "orientation session library",
          "new students orientation"]),
    _faq("FS23", "Reference and information services",
         "Can I get training on searching databases and using research tools?",
         "Kya mujhe databases search karne aur research tools ki training mil sakti hai?",
         "Yes. The library offers instructional programmes on information searching and research tools such as EndNote, Mendeley and SPSS, and on searching electronic databases — through orientation sessions, hands-on trainings, workshops and seminars. Send your request to library@uos.edu.pk. Deeper, paid specialist training is offered by the Research Support Lab.",
         "Ji haan. Library information searching aur research tools (jaise EndNote, Mendeley aur SPSS) aur electronic databases search karne par instructional programmes pesh karti hai — orientation sessions, hands-on trainings, workshops aur seminars ke zariye. Apni request library@uos.edu.pk par bhejein. Gehri, paid specialist training Research Support Lab deta hai.",
         SRC_INFO, STATUS_VERIFIED,
         ["training on searching databases", "searching databases training", "research tools training",
          "databases search training", "information literacy training"]),
    _faq("FS24", "Reference and information services",
         "Does the library offer book-searching assistance?",
         "Kya library book-searching assistance deti hai?",
         "Yes. If an item cannot be found on the shelf, inquire at the Circulation Desk — a search will be conducted, you will be notified once the item is located, and it will be held at the Circulation Desk for you to pick up within two days.",
         "Ji haan. Agar koi item shelf par na mile to Circulation Desk par maloom karein — item ki search ki jayegi, milne par aap ko ittila di jayegi, aur woh Circulation Desk par rakhi jayegi taake aap do din ke andar use le lein.",
         SRC_INFO, STATUS_VERIFIED,
         ["book-searching assistance", "book searching assistance", "book search assistance service",
          "assistance finding a book"]),
    _faq("FS25", "Reference and information services",
         "Can the library prepare a bibliography for my course or research?",
         "Kya library mere course ya research ke liye bibliography bana sakti hai?",
         "Yes. Under its instructional support service, library staff can create subject-specific bibliographies on users' demand — provided to faculty for course planning and to students for research projects and assignments.",
         "Ji haan. Instructional support service ke tehat library staff users ki demand par subject-specific bibliographies bana sakte hain — faculty ko course planning ke liye aur students ko research projects aur assignments ke liye di jati hain.",
         SRC_INFO, STATUS_VERIFIED,
         ["prepare a bibliography", "bibliography for my course", "bibliography bana sakti",
          "subject-specific bibliographies", "create a bibliography"]),
    _faq("FS26", "Reference and information services",
         "What is the SDI (Selective Dissemination of Information) service?",
         "SDI (Selective Dissemination of Information) service kya hai?",
         "Through the library portal, the SDI service keeps you informed about new additions to the library collection by saving your searches and delivering updates at regular intervals.",
         "Library portal ke zariye SDI service aap ko library collection mein naye izafon se agah rakhti hai — aap ki searches save karke regular intervals par updates bheji jati hain.",
         SRC_INFO, STATUS_VERIFIED,
         ["sdi service", "selective dissemination", "dissemination of information service",
          "sdi kya hai"]),
]

FAQS += [
    # ============ Category 4: Research Support Lab (12) ==================
    _faq("FS27", "Research Support Lab",
         "What is the Research Support Lab?",
         "Research Support Lab kya hai?",
         "The Research Support Lab, housed in the Digital Commons of the library, supports researchers of the UOS community — especially graduate students and faculty — with specialized resources, personalized consultation, workshops and paid trainings, including academic writing and thesis writing. The published contact person is Mr. Javed Iqbal, Assistant Librarian (Research Support and Faculty Liaison).",
         "Research Support Lab, jo library ke Digital Commons mein waqe hai, UOS community ke researchers — khaas tor par graduate students aur faculty — ko specialized resources, personalized consultation, workshops aur paid trainings deta hai, jin mein academic writing aur thesis writing bhi shamil hain. Published contact person Mr. Javed Iqbal, Assistant Librarian (Research Support and Faculty Liaison) hain.",
         SRC_RSL, STATUS_VERIFIED,
         ["research support lab", "support lab kya hai", "what is the research support",
          "research support lab kya", "help with research", "get help with research",
          "research mein madad", "research help chahiye"]),
    _faq("FS28", "Research Support Lab",
         "Can I get help with literature searching for my research?",
         "Kya mujhe apni research ke liye literature searching mein madad mil sakti hai?",
         "Yes. Subject-specific literature searching is one of the Research Support Lab's training areas, and the library's literature-search assistance service can also collaborate on literature reviews, systematic reviews and meta-analyses, including search strategies and PRISMA diagrams — email library@uos.edu.pk.",
         "Ji haan. Subject-specific literature searching Research Support Lab ke training areas mein se aik hai, aur library ki literature-search assistance service literature reviews, systematic reviews aur meta-analyses par bhi taawun kar sakti hai, search strategies aur PRISMA diagrams samait — library@uos.edu.pk par email karein.",
         SRC_RSL, STATUS_VERIFIED,
         ["help with literature searching", "literature searching help", "literature search assistance",
          "literature searching mein madad"]),
    _faq("FS29", "Research Support Lab",
         "Does the Research Support Lab offer EndNote training?",
         "Kya Research Support Lab EndNote training deta hai?",
         "Yes. Citation management using EndNote (or Mendeley) is one of the Research Support Lab's paid training topics.",
         "Ji haan. EndNote (ya Mendeley) se citation management Research Support Lab ke paid training topics mein se aik hai.",
         SRC_RSL, STATUS_VERIFIED,
         ["endnote training", "endnote ki training", "training in endnote", "learn endnote"]),
    _faq("FS30", "Research Support Lab",
         "Can I learn Mendeley at the Research Support Lab?",
         "Kya main Research Support Lab mein Mendeley seekh sakta hun?",
         "Yes. The Research Support Lab offers training in citation management using Mendeley (or EndNote) as a paid training topic.",
         "Ji haan. Research Support Lab Mendeley (ya EndNote) se citation management ki training deta hai, aik paid training topic ke tor par.",
         SRC_RSL, STATUS_VERIFIED,
         ["learn mendeley", "mendeley training", "mendeley seekh sakta", "training in mendeley"]),
    _faq("FS31", "Research Support Lab",
         "Can I get help with APA or Harvard referencing?",
         "Kya mujhe APA ya Harvard referencing mein madad mil sakti hai?",
         "Yes. Referencing styles — APA, Harvard, etc. — are one of the Research Support Lab's paid training topics.",
         "Ji haan. Referencing styles — APA, Harvard, waghera — Research Support Lab ke paid training topics mein se aik hain.",
         SRC_RSL, STATUS_VERIFIED,
         ["apa or harvard referencing", "help with referencing", "apa referencing help",
          "harvard referencing", "referencing styles help"]),
    _faq("FS32", "Research Support Lab",
         "Does the lab offer training on plagiarism avoidance and Turnitin usage?",
         "Kya lab plagiarism avoidance aur Turnitin usage ki training deta hai?",
         "Yes. 'Plagiarism Avoidance' and 'Turnitin Usage' are both listed among the Research Support Lab's paid training topics.",
         "Ji haan. 'Plagiarism Avoidance' aur 'Turnitin Usage' dono Research Support Lab ke paid training topics mein darj hain.",
         SRC_RSL, STATUS_VERIFIED,
         ["plagiarism avoidance training", "turnitin usage training", "plagiarism awareness training",
          "training on plagiarism"]),
    _faq("FS33", "Research Support Lab",
         "Can I get help writing my research proposal or synopsis?",
         "Kya mujhe research proposal ya synopsis likhne mein madad mil sakti hai?",
         "Yes. Research proposal or synopsis writing is one of the Research Support Lab's paid training topics, along with research methodology.",
         "Ji haan. Research proposal ya synopsis writing Research Support Lab ke paid training topics mein se aik hai, research methodology ke sath.",
         SRC_RSL, STATUS_VERIFIED,
         ["research proposal writing help", "help writing my research proposal", "synopsis writing help",
          "proposal likhne mein madad"]),
    _faq("FS34", "Research Support Lab",
         "Can the lab help me with my literature review?",
         "Kya lab meri literature review mein madad kar sakta hai?",
         "Yes. 'Literature Review using NVivo or Qiqqa' is one of the Research Support Lab's paid training topics.",
         "Ji haan. 'Literature Review using NVivo or Qiqqa' Research Support Lab ke paid training topics mein se aik hai.",
         SRC_RSL, STATUS_VERIFIED,
         ["help with my literature review", "literature review help", "literature review mein madad",
          "help me with literature review"]),
    _faq("FS35", "Research Support Lab",
         "Does the lab train on systematic reviews and meta-analysis?",
         "Kya lab systematic reviews aur meta-analysis ki training deta hai?",
         "Yes. 'How to Conduct Systematic Reviews?' and 'How to Conduct Meta Analysis?' are both Research Support Lab paid training topics, as is scientometric analysis.",
         "Ji haan. 'How to Conduct Systematic Reviews?' aur 'How to Conduct Meta Analysis?' dono Research Support Lab ke paid training topics hain, scientometric analysis bhi.",
         SRC_RSL, STATUS_VERIFIED,
         ["systematic reviews and meta-analysis", "systematic review training", "meta-analysis training",
          "meta analysis ki training"]),
    _faq("FS36", "Research Support Lab",
         "Can I get training in research methodology or online surveys?",
         "Kya mujhe research methodology ya online surveys ki training mil sakti hai?",
         "Yes. Research Methodology and 'How to conduct an online survey using Google Docs or Survey Monkey' are both Research Support Lab paid training topics.",
         "Ji haan. Research Methodology aur 'Google Docs ya Survey Monkey se online survey kaise conduct karein' dono Research Support Lab ke paid training topics hain.",
         SRC_RSL, STATUS_VERIFIED,
         ["research methodology training", "training in research methodology", "online survey training",
          "methodology ki training"]),
    _faq("FS37", "Research Support Lab",
         "Does the lab offer SPSS, SmartPLS, NVivo or MaxQDA training?",
         "Kya lab SPSS, SmartPLS, NVivo ya MaxQDA ki training deta hai?",
         "Yes. Quantitative data analysis using SPSS, SmartPLS, etc., and qualitative data analysis using NVivo, MaxQDA, Dedoose, etc., are Research Support Lab paid training topics.",
         "Ji haan. SPSS, SmartPLS waghera se quantitative data analysis, aur NVivo, MaxQDA, Dedoose waghera se qualitative data analysis, Research Support Lab ke paid training topics hain.",
         SRC_RSL, STATUS_VERIFIED,
         ["spss smartpls nvivo", "spss training", "smartpls training", "nvivo or maxqda training",
          "maxqda ki training", "data analysis training spss", "spss ki training",
          "spss seekhna hai"]),
    _faq("FS38", "Research Support Lab",
         "How much does Research Support Lab training cost?",
         "Research Support Lab ki training ki fees kitni hai?",
         f"The Research Support Lab's trainings are paid, but the exact fees are not published on the lab's page checked. Please contact the library for current fees: {CONTACT_LINE}",
         f"Research Support Lab ki trainings paid hain, lekin exact fees lab ke page par publish nahi hain jo check kiya gaya. Current fees ke liye library se rabta karein: {CONTACT_LINE}",
         SRC_RSL, STATUS_NOT_PUBLISHED,
         ["training cost", "lab training fees", "research support lab fees", "training ki fees kitni",
          "how much does the training cost", "paid training fees", "is there any fee",
          "fee for the research support", "fee for the training", "any fee for"]),

    # ============ Category 5: Digital Commons and Wi-Fi (6) ===============
    _faq("FS39", "Digital Commons and Wi-Fi",
         "Does the library have Wi-Fi?",
         "Kya library mein Wi-Fi hai?",
         "Yes. Wireless internet connectivity is available on all floors of the library for users with their own devices (laptops, notebooks, smartphones, etc.).",
         "Ji haan. Library ki tamam floors par wireless internet connectivity available hai un users ke liye jin ke pas apne devices (laptops, notebooks, smartphones waghera) hon.",
         SRC_INFO, STATUS_VERIFIED,
         ["library have wi-fi", "library have wifi", "does the library have wi", "wifi hai library",
          "wi fi hai", "library mein wifi"]),
    _faq("FS40", "Digital Commons and Wi-Fi",
         "How do I connect to the library Wi-Fi — what is the password?",
         "Main library Wi-Fi se kaise connect karun — password kya hai?",
         f"Wi-Fi is available on all floors, but the login credentials and connection procedure are not published on the library pages checked, and I cannot invent them. Please ask at the Information Desk or contact the library: {CONTACT_LINE}",
         f"Wi-Fi tamam floors par available hai, lekin login credentials aur connection procedure library pages par publish nahi hain jo check kiye gaye, aur main woh invent nahi kar sakta. Meherbani karke Information Desk se poochein ya library se rabta karein: {CONTACT_LINE}",
         SRC_INFO, STATUS_NOT_PUBLISHED,
         ["connect to the library wi-fi", "wifi password", "wi-fi password", "wifi se connect",
          "wifi ka password", "how do i connect to wifi", "wifi login"]),
    _faq("FS41", "Digital Commons and Wi-Fi",
         "Can I use computers in the library?",
         "Kya main library mein computers use kar sakta hun?",
         "Yes. The Digital Commons (first floor) has the latest computer systems and 40 seats, and it can be used by all library users for academic work.",
         "Ji haan. Digital Commons (first floor) mein latest computer systems aur 40 seats hain, aur yeh tamam library users academic kaam ke liye use kar sakte hain.",
         SRC_SPACES, STATUS_VERIFIED,
         ["use computers in the library", "can i use computers", "computers use kar sakta",
          "use the computers in library", "library computers use"]),
    _faq("FS42", "Digital Commons and Wi-Fi",
         "Can I use the library Wi-Fi on my own laptop or phone?",
         "Kya main apne laptop ya phone par library Wi-Fi use kar sakta hun?",
         "Yes. The library's Wi-Fi is for users' own digital devices — laptops, notebooks, smartphones and similar devices with a built-in wireless adaptor. Login details are not published; ask at the Information Desk.",
         "Ji haan. Library ki Wi-Fi users ke apne digital devices ke liye hai — laptops, notebooks, smartphones aur is jaisi devices jin mein built-in wireless adaptor ho. Login details publish nahi hain; Information Desk se poochein.",
         SRC_INFO, STATUS_VERIFIED,
         ["wifi on my own laptop", "wi-fi on my laptop", "apne laptop par wifi", "wifi on my phone",
          "use wifi on my device"]),
    _faq("FS43", "Digital Commons and Wi-Fi",
         "Where is the Digital Commons?",
         "Digital Commons kahan hai?",
         "The Digital Commons is on the first floor of the library. The Research Support Lab is housed in the Digital Commons.",
         "Digital Commons library ke first floor par hai. Research Support Lab bhi Digital Commons mein hi waqe hai.",
         SRC_COC, STATUS_VERIFIED,
         ["where is the digital commons", "digital commons kahan hai", "digital commons location",
          "digital commons where"]),
    _faq("FS44", "Digital Commons and Wi-Fi",
         "Are trainings and workshops held in the Digital Commons?",
         "Kya Digital Commons mein trainings aur workshops hote hain?",
         "Yes. The Digital Commons is used to maximize digital information resources and to hold research support trainings and workshops; the Research Support Lab is housed there.",
         "Ji haan. Digital Commons digital information resources ko maximize karne aur research support trainings aur workshops ke liye use hota hai; Research Support Lab bhi wahin waqe hai.",
         SRC_SPACES, STATUS_VERIFIED,
         ["trainings in the digital commons", "workshops held in digital", "digital commons workshops",
          "digital commons mein trainings"]),

    # ============ Category 6: Printing and multimedia services (5) =======
    _faq("FS45", "Printing and multimedia services",
         "Does the library offer printing?",
         "Kya library printing ki sahulat deti hai?",
         "Yes. Photocopying and printing are available at the library on the second floor (short range). Prices are not published on the library pages checked — please ask at the library.",
         "Ji haan. Library mein second floor par photocopying aur printing available hai (short range). Prices library pages par publish nahi hain jo check kiye gaye — meherbani karke library se poochein.",
         SRC_MAIN, STATUS_VERIFIED,
         ["library offer printing", "does the library offer printing", "printing ki sahulat",
          "offer photocopying", "printing available in library"]),
    _faq("FS46", "Printing and multimedia services",
         "Where are the photocopy machines and how many are there?",
         "Photocopy machines kahan hain aur kitni hain?",
         "There are two photocopying machines, located on the second floor of the library.",
         "Do photocopying machines hain, jo library ke second floor par waqe hain.",
         SRC_MAIN, STATUS_VERIFIED,
         ["photocopy machines", "where are the photocopy", "photocopy machines kahan",
          "how many photocopy machines", "photocopy kahan hogi"]),
    _faq("FS47", "Printing and multimedia services",
         "What are the photocopy or printing charges?",
         "Photocopy ya printing ke charges kya hain?",
         f"Photocopy and printing charges are not published on the library pages checked, so I cannot give you a price. Please ask at the library (second floor) or contact: {CONTACT_LINE}",
         f"Photocopy aur printing ke charges library pages par publish nahi hain jo check kiye gaye, is liye main price nahi de sakta. Meherbani karke library (second floor) se poochein ya rabta karein: {CONTACT_LINE}",
         SRC_MAIN, STATUS_NOT_PUBLISHED,
         ["photocopy charges", "printing charges", "photocopy ke charges", "printing ke charges",
          "cost of photocopy", "photocopy price"]),
    _faq("FS48", "Printing and multimedia services",
         "Where is the AV / multimedia lab?",
         "AV / multimedia lab kahan hai?",
         "The AV/multimedia lab is on the first floor, Hall-A, of the library.",
         "AV/multimedia lab library ke first floor, Hall-A mein hai.",
         SRC_HOME, STATUS_VERIFIED,
         ["multimedia lab", "av lab kahan", "where is the av", "av multimedia lab",
          "audio visual lab"]),
    _faq("FS49", "Printing and multimedia services",
         "Can the staff switch the discussion room LED on or off for us?",
         "Kya staff hamare liye discussion room ki LED on ya off kar sakte hain?",
         "Yes. Under the library's multimedia service, users can request the library staff to switch the LEDs in the discussion rooms on or off. The LEDs can be connected via Wi-Fi and Bluetooth for group presentations.",
         "Ji haan. Library ki multimedia service ke tehat users library staff se request kar sakte hain ke woh discussion rooms ki LEDs on ya off kar dein. LEDs group presentations ke liye Wi-Fi aur Bluetooth se connect ho sakti hain.",
         SRC_INFO, STATUS_VERIFIED,
         ["staff switch the led", "led on or off for us", "discussion room led on",
          "led on kar sakte", "switch the discussion room led"]),

    # ============ Category 7: Turnitin and plagiarism services (5) =======
    _faq("FS50", "Turnitin and plagiarism services",
         "Does the library provide Turnitin?",
         "Kya library Turnitin provide karti hai?",
         "Yes. The library provides a similarity checking service using Turnitin for graduate students of the UOS community, to ensure academic and research integrity.",
         "Ji haan. Library UOS community ke graduate students ke liye Turnitin se similarity checking service faraham karti hai, academic aur research integrity ko yaqeeni banane ke liye.",
         SRC_INFO, STATUS_VERIFIED,
         ["library provide turnitin", "does the library provide turnitin", "turnitin service library",
          "library turnitin deti", "provide turnitin"]),
    _faq("FS51", "Turnitin and plagiarism services",
         "Who can use the Turnitin similarity checking service?",
         "Turnitin similarity checking service kaun use kar sakta hai?",
         "It is for research students of the UOS community: MS/MPhil and PhD students need a similarity clearance certificate before submitting their thesis.",
         "Yeh UOS community ke research students ke liye hai: MS/MPhil aur PhD students ko apni thesis submit karne se pehle similarity clearance certificate lazmi hai.",
         SRC_INFO, STATUS_VERIFIED,
         ["who can use the turnitin", "use turnitin similarity", "turnitin kaun use kar sakta",
          "turnitin service for students"]),
    _faq("FS52", "Turnitin and plagiarism services",
         "How do I get a Turnitin check for my thesis?",
         "Main apni thesis ke liye Turnitin check kaise karwaun?",
         "Submit an application on the prescribed form for similarity checking through the proper channel, and the similarity report is issued the same way. The published focal person is Dr Ghulam Mustafa, Deputy Chief Librarian — ghulam.mustafa@uos.edu.pk. This chatbot cannot run Turnitin checks.",
         "Similarity checking ke liye prescribed form par proper channel se application jama karayein, aur similarity report bhi usi tareeqay se milti hai. Published focal person Dr Ghulam Mustafa, Deputy Chief Librarian hain — ghulam.mustafa@uos.edu.pk. Yeh chatbot Turnitin checks nahi kar sakta.",
         SRC_INFO, STATUS_VERIFIED,
         ["get a turnitin check", "turnitin check for my thesis", "turnitin check kaise",
          "apply for turnitin", "similarity checking apply", "how do i get turnitin",
          "similarity check kaise", "thesis ke liye similarity", "similarity check karwaun"]),
    _faq("FS53", "Turnitin and plagiarism services",
         "What similarity percentage is allowed in Turnitin?",
         "Turnitin mein kitni similarity percentage allowed hai?",
         f"The allowed similarity threshold is not published on the library pages checked, so I cannot state a percentage. Please ask the focal person, Dr Ghulam Mustafa (ghulam.mustafa@uos.edu.pk), or contact the library: {CONTACT_LINE}",
         f"Allowed similarity threshold library pages par publish nahi hai jo check kiye gaye, is liye main koi percentage nahi bata sakta. Meherbani karke focal person Dr Ghulam Mustafa (ghulam.mustafa@uos.edu.pk) se poochein, ya library se rabta karein: {CONTACT_LINE}",
         SRC_INFO, STATUS_NOT_PUBLISHED,
         ["similarity percentage allowed", "similarity percentage limit", "turnitin threshold",
          "kitni similarity allowed", "similarity limit turnitin"]),
    _faq("FS54", "Turnitin and plagiarism services",
         "Does Turnitin checking cost anything, and how long does it take?",
         "Kya Turnitin checking ki koi fees hai, aur is mein kitna time lagta hai?",
         f"Charges and turnaround time for similarity checking are not published on the library pages checked. Please contact the library or the focal person for current details: {CONTACT_LINE}",
         f"Similarity checking ke charges aur turnaround time library pages par publish nahi hain jo check kiye gaye. Current details ke liye library ya focal person se rabta karein: {CONTACT_LINE}",
         SRC_INFO, STATUS_NOT_PUBLISHED,
         ["turnitin checking cost", "turnitin fees", "turnitin kitna time", "turnitin charges",
          "how long does turnitin take"]),

    # ============ Category 8: Document delivery and inter-library loan (6)
    _faq("FS55", "Document delivery and inter-library loan",
         "Can I get a book from another library?",
         "Kya main kisi doosri library se kitab mangwa sakta hun?",
         "Yes. Through inter-library loan (ILL), if a particular item is not available in the library's collection, the library makes arrangements to acquire it from other libraries when a user makes such a request.",
         "Ji haan. Inter-library loan (ILL) ke zariye, agar koi item library ki collection mein available na ho to library user ki request par use doosri libraries se mangwane ke intizamat karti hai.",
         SRC_INFO, STATUS_VERIFIED,
         ["book from another library", "get a book from another", "doosri library se kitab",
          "book from other library", "mangwa sakta hun kitab", "doosri library se mil",
          "doosri library se mangwana"]),
    _faq("FS56", "Document delivery and inter-library loan",
         "What is inter-library loan (ILL)?",
         "Inter-library loan (ILL) kya hai?",
         "Inter-library loan is a library service: if a particular item is not available in our collection, the library arranges to acquire it from other libraries, on a user's request.",
         "Inter-library loan aik library service hai: agar koi item hamari collection mein available na ho, to library user ki request par use doosri libraries se mangwane ka intizam karti hai.",
         SRC_INFO, STATUS_VERIFIED,
         ["what is inter-library loan", "inter library loan kya", "what is ill",
          "inter-library loan service"]),
    _faq("FS57", "Document delivery and inter-library loan",
         "What is electronic document delivery?",
         "Electronic document delivery kya hai?",
         "The UOS Libraries offer electronic access to documents and journal articles that are not available locally: they obtain these resources through the internet from international service providers, to assist researchers in their projects.",
         "UOS Libraries un documents aur journal articles tak electronic rasai deti hain jo locally available na hon: woh ye resources internet ke zariye international service providers se hasil karti hain, researchers ki un ke projects mein madad ke liye.",
         SRC_INFO, STATUS_VERIFIED,
         ["electronic document delivery", "document delivery service", "document delivery kya",
          "electronic document delivery service"]),
    _faq("FS58", "Document delivery and inter-library loan",
         "Can I get a journal article that is not available in this library?",
         "Kya mujhe woh journal article mil sakta hai jo is library mein available nahi?",
         "Yes, possibly. Through electronic document delivery, the UOS Libraries obtain documents and journal articles that are not available locally, via international service providers — the service is intended to assist researchers. Ask the library to request it; this chatbot cannot place the request for you.",
         "Ji haan, mumkin hai. Electronic document delivery ke zariye UOS Libraries woh documents aur journal articles hasil karti hain jo locally available na hon, international service providers ke zariye — yeh service researchers ki madad ke liye hai. Library se request karne ko kahein; yeh chatbot aap ke liye request nahi kar sakta.",
         SRC_INFO, STATUS_VERIFIED,
         ["journal article not available", "article not available in this library",
          "journal article mil sakta", "get a journal article"]),
    _faq("FS59", "Document delivery and inter-library loan",
         "How do I request an inter-library loan or document delivery?",
         "Main inter-library loan ya document delivery ki request kaise karun?",
         f"Make your request to the library — the Information Services page confirms both services exist for users on request, but it does not publish a step-by-step form or procedure. Ask at the Information Desk / Circulation Desk or email: {CONTACT_LINE}",
         f"Apni request library ko karein — Information Services page confirm karta hai ke dono services users ki request par available hain, lekin koi step-by-step form ya procedure publish nahi hai. Information Desk / Circulation Desk par poochein ya email karein: {CONTACT_LINE}",
         SRC_INFO, STATUS_GUIDANCE,
         ["request an inter-library loan", "request document delivery", "ill request kaise",
          "how do i request inter-library", "request kaise karun loan"]),
    _faq("FS60", "Document delivery and inter-library loan",
         "Can you place an inter-library loan request for me?",
         "Kya aap mere liye inter-library loan request kar sakte hain?",
         f"No — I cannot place requests, bookings or orders. Please make the request directly to the library: {CONTACT_LINE}, or ask at the Information Desk.",
         f"Nahi — main requests, bookings ya orders nahi kar sakta. Meherbani karke request seedha library ko karein: {CONTACT_LINE}, ya Information Desk par poochein.",
         SRC_INFO, STATUS_GUIDANCE,
         ["place an inter-library loan request for me", "place ill request for me",
          "mere liye ill request", "can you place a request for me"]),
]


# ---------------- Matching (same strict design as library_faq.py) ------
for _f in FAQS:
    _f["_q_words"] = (_content_words(_f["q_en"]), _content_words(_f["q_ru"]))


def find_service_faq(text):
    """Return the single best-matching services FAQ dict, or None."""
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
        # Containment bonus grows with the NUMBER of matched content
        # words, so a longer, more specific canonical question (e.g.
        # "...offer EndNote training?") beats a short generic one
        # (e.g. "What is the Research Support Lab?") on its own turf.
        # The coverage condition stops a short generic question from
        # claiming a longer user question that merely mentions its
        # words (e.g. the lab's name inside a fees question).
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


def service_faq_answer(text, roman_urdu=False):
    """Full services-FAQ answer (with source link), or None."""
    faq = find_service_faq(text)
    if faq is None:
        return None
    if not roman_urdu:
        words = set(_normalize(text).split())
        roman_urdu = len(words & _FAQ_URDU_WORDS) >= 2
    body = faq["a_ru"] if roman_urdu else faq["a_en"]
    return f"{body}\n\nSource: {faq['source']}"
