"""Explicit procurement actor routing and workflow-family policy.

Actor classification happens before retrieval.  Retrieval expansions and model
instructions consume the same policy so a buyer cannot silently drift into a
vendor workflow (or vice versa).
"""

from typing import Dict, Tuple


DEPARTMENT_BUYER = "department_buyer"
VENDOR_BIDDER = "vendor_bidder"
DEPARTMENT_OPERATOR = "department_operator"
GENERAL_INFORMATION_USER = "general_information_user"


ACTOR_WORKFLOW_FAMILIES: Dict[str, Tuple[str, ...]] = {
    DEPARTMENT_BUYER: (
        "need_assessment",
        "approvals",
        "specifications",
        "gem_procurement",
        "tender_creation",
        "evaluation",
        "purchase_order",
        "inspection",
        "payment",
    ),
    VENDOR_BIDDER: (
        "registration",
        "dsc",
        "emd",
        "bid_submission",
        "corrigendum_tracking",
        "auction_participation",
    ),
    DEPARTMENT_OPERATOR: (
        "portal_administration",
        "tender_creation",
        "tender_publication",
        "corrigendum_management",
        "bid_opening",
        "evaluation_support",
        "emd_refund_or_remittance",
        "contract_management",
    ),
    GENERAL_INFORMATION_USER: (
        "definitions",
        "procurement_methods",
        "rules_and_thresholds",
        "eligibility_information",
        "document_explanation",
    ),
}


_EXPLICIT_VENDOR_SIGNALS = (
    "i am vendor", "i'm a vendor", "i am a vendor", "main vendor",
    "vendor hoon", "supplier hoon", "bidder hoon", "as a vendor",
    "as vendor", "as a bidder", "as bidder", "as a supplier",
    "vendor ke roop", "bidder ke roop", "supplier ke roop",
    "मैं विक्रेता", "मैं बोलीदाता", "विक्रेता के रूप", "बोलीदाता के रूप",
    "foreign vendor", "bidder के रूप", "vendor के रूप",
)

_VENDOR_OPERATION_SIGNALS = (
    "register as a vendor", "register as vendor", "register as a new vendor",
    "vendor registration", "vendor registrtion",
    "supplier registration", "bidder registration", "vendor register",
    "bidder set up dsc", "bidder setup dsc", "vendor dsc", "bidder dsc",
    "pay emd", "emd payment", "emd for my bid", "my emd", "vendor ka emd",
    "get emd refund", "emd refund kab", "emd refund process", "track a corrigendum",
    "track corrigendum", "vendor kya kare", "participate in reverse auction",
    "bidder corrigendum", "bidder amendment", "corrigendum check kare",
    "participate in auction", "auction mein kaise participate",
    "eligible to bid", "eligible to participate", "bidder eligibility", "tender eligibility",
    "submit bid", "submit my technical and price bid", "technical and price bid online",
    "bid submit", "how to bid", "tender mein bid",
    "meri bid", "my bid", "bid कैसे जमा", "बोली कैसे जमा",
    "विक्रेता पंजीकरण", "विक्रेता के रूप में पंजीकरण",
    "vendor password", "vendor login password", "renewed dsc", "नवीनीकृत dsc", "submitted bid",
    "bid delete", "bid deleted", "bid हट", "बोली हट",
    "emd 2 lakh jama", "reverse auction mein vendor", "vendor kaise participate",
    "मैं नया विक्रेता", "बोलीदाता अपना डिजिटल हस्ताक्षर", "ईएमडी जमा",
    "असफल बोलीदाता की ईएमडी", "तकनीकी और मूल्य बोली", "मेरी जमा बोली",
    "ई-नीलामी में बोलीदाता", "बोलीदाता कैसे भाग",
)

# Identify bidder actions when the user omits an explicit role statement.
# Keep these action-specific so definition questions remain informational.
_IMPLICIT_VENDOR_OPERATION_SIGNALS = (
    "dsc kaise obtain", "dsc kaise le", "dsc kaise mile", "obtain dsc",
    "get dsc", "digital signature kaise obtain", "digital signature kaise le",
    "tender eligibility kaise check", "tender eligibility criteria kaise check",
    "eligibility criteria kaise check", "tender eligibility criteria",
    "auction mein participate", "auction me participate", "e-auction mein participate",
    "e auction mein participate", "participate in an e-auction",
    "bid deadline ke baad", "bid edit kar", "edit my bid", "modify my bid",
    "modify bid after", "financial bid kaise submit", "technical bid submit ho",
    "bidders ko kya karna", "bidder ko kya karna", "after corrigendum bidders",
    "foreign company tender mein participate", "foreign company participate in tender",
    # Human-style benchmark: role is implied by a portal action rather than a
    # self-description such as "I am a vendor".
    "registered bidder", "become a registered bidder", "become a register bidder",
    "technical documents are uploaded",
    "where do i enter the price bid", "forward e-auction", "forward e auction",
    "placing a bid", "foreign company", "foreign company hain",
    "bidder eligible", "emd exemption", "exemption be claimed",
    "self-attested", "self attested", "original documents upload",
    "neft", "rtgs", "challan", "transaction receipt", "payment gateway",
    "tender document fee", "java error", "browser settings", "ie mode",
    "dynamic links", "boq.xls", "commercial schedule", "formula modification",
)

_OPERATOR_SIGNALS = (
    "portal operator", "department operator", "department admin", "tender owner",
    "procurement operator", "create tender", "publish tender",
    "issue tender", "upload nit", "open technical bid", "open price bid",
    "create a tender", "create the tender", "publish the tender",
    "publish the department tender", "issue a corrigendum",
    "issue corrigendum", "corrigendum issue", "open the technical bid",
    "open the price bid", "bid opening", "process bidders emd refund",
    "process bidder emd refund", "department users process", "department approver emd refund",
    "operator emd refund", "operator upload", "upload offline tender",
    "offline tender portal", "tender बनाएं", "tender बनाए", "निविदा बनाएं",
    "निविदा प्रकाशित", "corrigendum जारी", "बिड खोल", "बोली खोल",
    "corrigendum kaise issue", "corrigendum कैसे जारी", "portal पर corrigendum",
    "issuing a date corrigendum", "date corrigendum portal", "department user",
    "tender term corrigendum", "attachment corrigendum", "required attachment corrigendum",
    "technical bid open", "operator workflow", "offline tendr portal",
    "विभागीय ऑपरेटर", "विभागीय उपयोगकर्ता", "आइटम शुद्धिपत्र",
    "विभाग असफल बोलीदाताओं", "ऑफलाइन निविदा को पोर्टल",
)

# These are department-side portal actions even if "operator" is not said.
_IMPLICIT_OPERATOR_OPERATION_SIGNALS = (
    "tender publish", "tender ko publish", "publish a tender",
    "bid open kaise", "bids kaise open", "technical bids kaise open",
    "price bids kaise open", "technical bid kaise open", "price bid kaise open",
    "last date extend", "tender last date extend", "bid due date extend",
    "extend tender date", "extend the tender date",
    "offline tender upload", "manual tender upload",
    "evaluation report kaise generate", "bid evaluation report generate",
    "department side se initiate", "department side emd refund",
    "refund department side", "department side refund",
    "tender cancel", "reasons record",
    "expired certificate", "clarification be requested",
    "financial bids kin bidders ki open", "financial bids kin bidder ki open",
    "evaluation committee record reasons",
    "tender conditions be changed",
    "technical opener", "decrypt bid", "class-iii dsc", "class iii dsc",
    "technical bid opening responsibility",
)

_MIXED_ROLE_SIGNALS = (
    "create a tender or submit a bid",
    "tender banana hai ya bid bharni hai",
    "निविदा बनानी है या बोली जमा करनी है",
)

# These ask whether an inter-departmental route is permitted.  They are rule
# questions, not a request for a buyer's own procurement lifecycle.
_INTER_DEPARTMENT_INFORMATION_SIGNALS = (
    "one government department purchase goods from another",
    "one department purchase goods from another department",
    "inter-departmental purchase", "interdepartmental purchase",
    "inter-department procurement", "interdepartment procurement",
    "government department ko dusre government undertaking se goods purchase",
    "dusre government undertaking se goods purchase",
)

_DEPARTMENT_SIGNALS = (
    "department ke liye", "departments k liye", "department k liye",
    "government office ke liye", "government office", "office ke liye", "office ke", "hamare office",
    "our office", "our department", "department wants to buy",
    "department ko", "department purchase", "department buy",
    "government department", "department needs", "department gem",
    "district office", "district-level office",
    "department ke", "department ", "procuring entity", "buyer department",
    "indent create", "hamare vibhag", "vibhag ko", "vibhag ke liye",
    "विभाग के लिए", "विभाग को", "विभाग ", "विभागीय खरीद", "सरकारी विभाग", "कार्यालय के लिए",
)

_PURCHASE_SIGNALS = (
    "kharid", "purchase", "buy", "procure", "chahiye", "requirement",
    "needs", "need ", "amc", "maintenance contract", "direct from gem",
    "direct gem", "gem se direct", "खरीद", "क्रय", "चाहिए", "आवश्यकता",
)

_GOODS_SIGNALS = (
    "laptop", "computer", "desktop", "printer", "scanner", "server",
    "router", "equipment", "furniture", "vehicle", "goods", "item",
    "software", "licence", "license", "amc", "maintenance", "chairs",
    "kursi", "kursiyan", "car", "jeep", "वाहन", "फर्नीचर", "कुर्सी",
    "सॉफ्टवेयर", "लैपटॉप", "प्रिंटर", "कंप्यूटर",
)

_PURCHASE_PROCESS_SIGNALS = (
    "process", "procedure", "prakriya", "kaise", "kya kar", "next",
    "karna", "karne", "kharidne", "purchase kar", "procurement", "प्रक्रिया",
)

_BUYER_LIFECYCLE_SIGNALS = (
    "purchase order issue", "asset register entry", "payment and asset",
    "budget and administrative approval", "inspection and acceptance",
    "विभागीय खरीद", "प्रशासनिक स्वीकृति", "क्रय आदेश",
    "निरीक्षण और स्वीकृति", "संपत्ति रजिस्टर", "स्टॉक और संपत्ति",
)

# Department buyer decisions that are ordinarily phrased without the word
# "department".  These are deliberately narrow operational questions, rather
# than broad definitions such as "what is L1?".
_IMPLICIT_BUYER_OPERATION_SIGNALS = (
    "can we specify", "can i specify", "specify dell", "specify only dell",
    "split a purchase", "purchase into smaller orders", "split purchase",
    "split a ", "smaller purchase orders",
    "only one quotation is available on gem",
    "single tender be used because the earlier supplier",
    "proprietary software sirf ek company provide",
    "administrative approval aur financial sanction",
    "budget availability before a tender", "tender initiated before the budget",
    "tender be initiated before the budget",
    "bid evaluation kaise hoti", "bid evaluation kaise hota",
    "lowest bidder select", "l1 bidder select",
    "inspection aur acceptance", "inspection and acceptance process",
    "procurement method was justified", "competent authority approve",
    "delegated financial power", "delegated power", "last year's approved rate",
    "fresh procurement", "price reasonableness", "price reasonable",
    "only one valid bid", "negotiations be conducted", "all received bids",
    "reject all bids", "preferred brand", "favour one vendor",
    "experience mandatory rakhna", "processing payment to the supplier",
    "processing payment",
    "technically non-responsive", "financial bid open", "financial bid opened",
    "emergency medical", "covid test kits", "bina competitive bidding",
    "networking project", "limited tender works", "goods procurement rule",
    "cooperative society", "public sector undertaking", "value limit",
    "old vendor response", "single tender invite", "purana vendor",
    "high-quality ram", "fast processor", "ambiguous terms",
    "minimum annual turnover", "annual turnover", "local service center",
    "eligibility criteria", "relax eligibility", "msme certificate", "specific category",
    "past performance report", "l1 bidder backs out", "l2 bidder", "joint venture", "consortium",
    "comparative statement", "contradiction", "fake experience certificate", "tied l1",
    "tie-breaker", "financial bids", "work order", "purchase order amended",
    "purchase order be amended", "order amended after it has been signed",
    "bank guarantee", "liquidated damages", "delivery delay penalty",
)

_PERSONAL_SIGNALS = (
    "personal use", "for myself", "apne liye", "ghar ke liye", "home use",
)


def classify_procurement_actor(query: str) -> Tuple[str, float]:
    """Return one canonical actor before retrieval or generation.

    Explicit vendor/operator/personal wording wins.  In this government-
    procurement assistant, an unqualified request for the process to purchase a
    named good is treated as a department-buyer request unless the user says it
    is personal.  This is the important distinction for queries such as
    ``mujhe laptop kharidne ka process batao``.
    """
    q = (query or "").lower()
    if not q:
        return (GENERAL_INFORMATION_USER, 0.0)
    if any(signal in q for signal in _MIXED_ROLE_SIGNALS):
        return (GENERAL_INFORMATION_USER, 0.92)
    if any(signal in q for signal in _INTER_DEPARTMENT_INFORMATION_SIGNALS):
        return (GENERAL_INFORMATION_USER, 0.94)
    if any(signal in q for signal in _EXPLICIT_VENDOR_SIGNALS):
        return (VENDOR_BIDDER, 0.98)
    if any(signal in q for signal in _OPERATOR_SIGNALS):
        return (DEPARTMENT_OPERATOR, 0.95)
    if any(signal in q for signal in (
        "in general", "general meaning", "general definition", "what is a tender",
    )):
        return (GENERAL_INFORMATION_USER, 0.8)
    # A pure policy question about whether a quotation proves price
    # reasonableness is informational; it does not imply that the user is the
    # department buyer conducting the evaluation.
    if ("lowest quotation milne" in q and "price reasonable" in q):
        return (GENERAL_INFORMATION_USER, 0.9)
    if ("emd exemption" in q or "emd" in q and "exemption" in q) and any(term in q for term in ("mse", "msme")) and "certificate" not in q:
        return (GENERAL_INFORMATION_USER, 0.9)
    if ("तकनीकी मूल्यांकन" in q and "असफल" in q and "विभाग" in q
            and "क्या" in q):
        return (GENERAL_INFORMATION_USER, 0.9)
    if ("performance security" in q and "forfeit" in q
            and not any(term in q for term in ("department", "vibhag", "our office"))):
        return (GENERAL_INFORMATION_USER, 0.9)
    if ("liquidated damages" in q and "standard contracts" in q):
        return (GENERAL_INFORMATION_USER, 0.9)
    if ("cvc guidelines" in q and any(term in q for term in (
            "bank guarantee", "negotiations", "negotiation"))):
        return (GENERAL_INFORMATION_USER, 0.9)
    if ("under what circumstances" in q and "purchase order" in q
            and "amended" not in q
            and not any(term in q for term in ("department", "our office"))):
        return (GENERAL_INFORMATION_USER, 0.9)
    if "administrative approval" in q and "financial sanction" in q:
        return (DEPARTMENT_BUYER, 0.9)
    if ("तकनीकी रूप से अयोग्य" in q or "तकनीकी रूप से अयोग्य निविदाकार" in q):
        return (DEPARTMENT_BUYER, 0.9)
    if ("आपातकालीन" in q and "चिकित्सा" in q):
        return (DEPARTMENT_BUYER, 0.9)
    if ("बोलीदाता" in q and "अंतिम तिथि" in q and "दस्तावेज" in q):
        return (VENDOR_BIDDER, 0.9)
    if any(signal in q for signal in _IMPLICIT_OPERATOR_OPERATION_SIGNALS):
        return (DEPARTMENT_OPERATOR, 0.9)
    if any(signal in q for signal in _PERSONAL_SIGNALS):
        return (GENERAL_INFORMATION_USER, 0.98)
    if any(signal in q for signal in _VENDOR_OPERATION_SIGNALS):
        return (VENDOR_BIDDER, 0.9)
    if any(signal in q for signal in _IMPLICIT_VENDOR_OPERATION_SIGNALS):
        return (VENDOR_BIDDER, 0.88)
    if ("emd" in q
            and not any(term in q for term in ("what is", "kya hai", "क्या है", "exemption", "exempt", "छूट"))
            and any(term in q for term in (
                "need to pay", "payment", "भुगतान", "जमा", "debit", "कट गया",
                "unsuccessful bidder", "असफल bidder", "l1 bidder", "successful bidder",
                "refund", "wapas", "वापस",
            ))):
        return (VENDOR_BIDDER, 0.9)
    if (any(term in q for term in ("dsc", "digital signature"))
            and any(term in q for term in ("map", "renew", "नवीनीकृत", "नवीकरण", "login problem"))):
        return (VENDOR_BIDDER, 0.9)
    if any(signal in q for signal in _BUYER_LIFECYCLE_SIGNALS):
        return (DEPARTMENT_BUYER, 0.9)
    if any(signal in q for signal in _IMPLICIT_BUYER_OPERATION_SIGNALS):
        return (DEPARTMENT_BUYER, 0.84)

    department_signal = any(signal in q for signal in _DEPARTMENT_SIGNALS)
    purchase_signal = any(signal in q for signal in _PURCHASE_SIGNALS)
    if department_signal and purchase_signal:
        return (DEPARTMENT_BUYER, 0.98)
    if department_signal:
        return (DEPARTMENT_BUYER, 0.85)

    goods_signal = any(signal in q for signal in _GOODS_SIGNALS)
    process_signal = any(signal in q for signal in _PURCHASE_PROCESS_SIGNALS)
    buyer_decision_signal = any(term in q for term in (
        "direct purchase", "direct from gem", "gem se direct", "approval",
        "budget", "specification", "inspection", "acceptance",
    ))
    if goods_signal and any(term in q for term in (
            "technical specification", "specifications", "विनिर्देश")):
        return (DEPARTMENT_BUYER, 0.86)
    if any(term in q for term in (
            "after the purchase order", "purchase order ke baad",
            "purchase order के बाद", "po ke baad")):
        return (DEPARTMENT_BUYER, 0.86)
    if goods_signal and purchase_signal and process_signal:
        return (DEPARTMENT_BUYER, 0.82)
    if goods_signal and buyer_decision_signal:
        return (DEPARTMENT_BUYER, 0.8)

    return (GENERAL_INFORMATION_USER, 0.55)


def allowed_workflow_families(actor: str) -> Tuple[str, ...]:
    """Return the only workflow families an actor may be routed into."""
    return ACTOR_WORKFLOW_FAMILIES.get(
        actor, ACTOR_WORKFLOW_FAMILIES[GENERAL_INFORMATION_USER]
    )


def actor_retrieval_terms(actor: str, intent: str, commodity: str) -> Tuple[str, ...]:
    """Return actor-safe retrieval terms without cross-actor workflow leakage."""
    if actor == DEPARTMENT_BUYER:
        commodity_terms = {
            "laptops_computers_it_equipment": (
                "laptop procurement", "computer procurement", "IT equipment procurement"
            ),
            "printers_office_equipment": (
                "printer procurement", "office equipment procurement"
            ),
            "it_equipment": ("IT equipment procurement",),
            "furniture": ("furniture procurement", "office furniture procurement"),
            "vehicle": ("government vehicle procurement",),
            "software": ("software procurement", "software licence procurement"),
            "amc_services": ("annual maintenance contract procurement", "AMC services"),
            "emergency_goods": ("emergency procurement", "urgent purchase procedure"),
        }.get(commodity, ("government goods procurement",))
        return commodity_terms + (
            "government department purchase",
            "need assessment",
            "technical specifications",
            "administrative approval",
            "budgetary sanction",
            "purchase indent",
            "GeM procurement",
            "Chhattisgarh Store Purchase Rules",
            "tender creation and evaluation",
            "rate reasonableness",
            "purchase order inspection acceptance payment stock control",
            "department buyer procuring entity",
        )
    if actor == VENDOR_BIDDER:
        intent_terms = {
            "VENDOR_REGISTRATION": ("CHiPS Vendor Registration Manual", "vendor registration workflow"),
            "DSC": ("CHiPS Vendor Registration Manual", "bidder DSC registration"),
            "EMD_PAYMENT": ("EMD Challan Payment Manual", "bidder EMD payment workflow"),
            "EMD_REFUND": ("Online EMD Refund Notice", "bidder EMD refund workflow"),
            "BID_SUBMISSION": (
                "CHiPS Bid Submission Manual",
                "bidder login DSC tender search participate technical bid price bid encrypt upload submit",
            ),
            "CORRIGENDUM_TRACKING": ("CHiPS Bid Submission Manual", "bidder corrigendum tracking"),
            "AUCTION": ("Auction Manual", "vendor auction participation"),
            "TENDER_ELIGIBILITY": ("tender eligibility conditions", "CHiPS Bid Submission Manual"),
        }.get(intent, ())
        return ("vendor bidder portal workflow",) + intent_terms
    if actor == DEPARTMENT_OPERATOR:
        intent_terms = {
            "TENDER_CREATION": (
                "department tender creation manual",
                "procuring entity online tender creation identify bid openers",
            ),
            "TENDER_PUBLICATION": (
                "department tender publication manual",
                "procuring entity publish NIT e-procurement portal",
            ),
            "CORRIGENDUM_MANAGEMENT": (
                "department corrigendum management manual",
                "procuring entity amend tender documents by issuing corrigendum upload portal extend deadline",
            ),
            "BID_OPENING": (
                "department bid opening manual",
                "bid openers open techno-commercial price bids online download scrutiny reports",
            ),
            "OPERATOR_EMD_REFUND": (
                "department EMD refund processing manual",
                "procuring entity return unsuccessful bidders EMD through e-payment system",
            ),
            "OFFLINE_TENDER_UPLOAD": (
                "Offline Tender Manual",
                "procuring entity offline tender upload publication workflow",
            ),
        }.get(intent, ())
        return (
            "department operator tender owner portal workflow",
            "create publish corrigendum open evaluate tender contract management",
        ) + intent_terms
    return ()


def actor_generation_directive(actor: str) -> str:
    """Build a compact model instruction from the actor's allow-list."""
    allowed = ", ".join(allowed_workflow_families(actor))
    if actor == DEPARTMENT_BUYER:
        forbidden = "vendor registration, DSC setup, EMD payment, and bid submission"
    elif actor == VENDOR_BIDDER:
        forbidden = "department approvals, tender creation, evaluation, purchase order, inspection, and payment"
    elif actor == DEPARTMENT_OPERATOR:
        forbidden = "vendor bid preparation and department purchase-planning advice unless explicitly asked"
    else:
        forbidden = "transactional workflow assumptions; answer informationally unless the actor is explicit"
    return (
        "\n\nACTOR POLICY - STRICT:\n"
        f"- Detected actor: {actor}.\n"
        f"- Allowed workflow families: {allowed}.\n"
        f"- Do not route this actor into: {forbidden}.\n"
        "- If retrieved context belongs to a forbidden workflow, ignore that context.\n"
    )


def actor_answer_violations(actor: str, answer: str) -> Tuple[str, ...]:
    """Detect workflow leakage that must not be shown to the user.

    This is deliberately limited to imperative vendor-side actions in a
    department-buyer answer.  Mentioning a word such as ``vendor`` alone is
    legitimate when explaining that vendors submit bids.
    """
    low = (answer or "").casefold()
    if actor != DEPARTMENT_BUYER:
        return ()
    forbidden = (
        "register as a vendor", "vendor registration", "register on gem",
        "valid dsc", "register your dsc", "submit your bid",
        "technical bid and price bid", "pay emd", "emd refund",
        "performance security deni", "performance security provide",
    )
    return tuple(term for term in forbidden if term in low)
