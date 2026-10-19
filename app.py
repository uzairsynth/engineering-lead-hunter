import re
import time
from urllib.parse import urljoin, urlparse, urlunparse

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from ddgs import DDGS


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Engineering Business Lead Hunter",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Engineering Business Lead Hunter")

st.caption(
    "Find public engineering opportunities and enrich the best "
    "leads with company website, public business contact details "
    "and social presence."
)


# ============================================================
# SERVICES
# ============================================================

SERVICES = {

    "Mechanical Design": [
        "mechanical design",
        "mechanical designer",
        "mechanical engineer",
        "mechanism design",
        "machine design"
    ],

    "CAD / SolidWorks / Fusion 360": [
        "cad design",
        "solidworks",
        "fusion 360",
        "3d cad",
        "cad engineer"
    ],

    "Product Development": [
        "product development",
        "hardware product development",
        "prototype development",
        "product design",
        "hardware prototype",
        "dfm"
    ],

    "Robotics": [
        "robotics",
        "robotics engineer",
        "robot engineer",
        "robot integration",
        "robot development",
        "robotic system"
    ],

    "Humanoid Robotics": [
        "humanoid robot",
        "humanoid robotics",
        "biped robot",
        "humanoid development"
    ],

    "Robotic Arms / Grippers": [
        "robot arm",
        "robotic arm",
        "robotic hand",
        "robot gripper",
        "end effector",
        "manipulator"
    ],

    "Mechatronics": [
        "mechatronics",
        "mechatronics engineer",
        "electromechanical design",
        "mechatronic system"
    ],

    "ROS 2": [
        "ros 2",
        "ros2",
        "robot operating system",
        "nav2",
        "moveit",
        "urdf",
        "gazebo robotics"
    ],

    "Automation": [
        "automation",
        "industrial automation",
        "robotic automation",
        "machine automation",
        "automation engineer",
        "motion control"
    ],

    "PLC / HMI / Controls": [
        "plc",
        "hmi",
        "control systems",
        "industrial controls",
        "machine control"
    ],

    "Drones / UAV": [
        "drone",
        "uav",
        "uas",
        "aerial robotics",
        "quadcopter",
        "autonomous drone"
    ],

    "Drone Payload Integration": [
        "drone payload",
        "uav payload",
        "payload integration",
        "camera payload",
        "drone gimbal"
    ],

    "CNC Design": [
        "cnc design",
        "cnc machining",
        "machining design",
        "cam design",
        "machined parts"
    ],

    "Jigs / Fixtures / Tooling": [
        "fixture design",
        "jig design",
        "manufacturing fixture",
        "production tooling",
        "cnc fixture"
    ],

    "3D Printing / Prototyping": [
        "3d printing",
        "additive manufacturing",
        "rapid prototyping",
        "prototype manufacturing"
    ],

    "Embedded Systems": [
        "embedded systems",
        "embedded engineer",
        "firmware",
        "microcontroller",
        "embedded development"
    ],

    "Motor / Actuator Control": [
        "motor control",
        "servo control",
        "actuator integration",
        "bldc control",
        "motion controller"
    ],

    "Computer Vision": [
        "computer vision",
        "machine vision",
        "robot vision",
        "visual inspection",
        "opencv"
    ],

    "Simulation / FEA": [
        "fea",
        "finite element analysis",
        "ansys",
        "structural analysis",
        "engineering simulation"
    ],

    "Robot Simulation": [
        "gazebo",
        "isaac sim",
        "robot simulation",
        "digital twin robotics",
        "urdf simulation",
        "isaac lab"
    ]
}


# ============================================================
# SEARCH SOURCES
# ============================================================

CHANNELS = [
    "General Web",
    "Company Hiring",
    "Contract / Consulting",
    "Startup Opportunities",
    "Product Development Projects",
    "Freelance Projects",
    "Lever Jobs",
    "Greenhouse Jobs",
    "Ashby Jobs",
    "Y Combinator",
    "Wellfound",
    "RFP / RFQ / Tender"
]


LOCATIONS = [
    "Worldwide",
    "Remote",
    "USA",
    "Canada",
    "United Kingdom",
    "Germany",
    "France",
    "Netherlands",
    "Europe",
    "UAE",
    "Saudi Arabia",
    "Qatar",
    "Australia",
    "Singapore",
    "Pakistan",
    "India"
]


TIME_MAP = {
    "Past week": "w",
    "Past month": "m",
    "Past year": "y",
    "Any time": None
}


# ============================================================
# DOMAINS
# ============================================================

AGGREGATORS = {
    "lever.co",
    "greenhouse.io",
    "ashbyhq.com",
    "wellfound.com",
    "linkedin.com",
    "indeed.com",
    "glassdoor.com",
    "ziprecruiter.com",
    "ycombinator.com",
    "upwork.com",
    "freelancer.com",
    "workable.com",
    "smartrecruiters.com",
    "builtin.com"
}


SOCIAL_DOMAINS = {
    "linkedin.com",
    "x.com",
    "twitter.com",
    "instagram.com",
    "facebook.com",
    "youtube.com",
    "youtu.be",
    "github.com",
    "tiktok.com"
}


# ============================================================
# SCORING WORDS
# ============================================================

HIGH_INTENT = [
    "hiring",
    "looking for",
    "seeking",
    "need engineer",
    "contractor",
    "contract position",
    "freelance",
    "consultant",
    "consulting",
    "outsourcing",
    "outsource",
    "partner",
    "vendor",
    "prototype",
    "rfp",
    "rfq",
    "tender",
    "job opening",
    "vacancy",
    "apply"
]


CONTRACT_TERMS = [
    "contract",
    "contractor",
    "freelance",
    "consultant",
    "consulting",
    "outsourcing",
    "outsource"
]


STARTUP_TERMS = [
    "startup",
    "start-up",
    "venture",
    "seed",
    "series a",
    "series b",
    "founder",
    "early stage"
]


PRODUCT_TERMS = [
    "prototype",
    "product development",
    "hardware",
    "robot",
    "device",
    "machine",
    "manufacturing"
]


NEGATIVE_TERMS = [
    "course",
    "tutorial",
    "training course",
    "certification",
    "salary guide",
    "resume example",
    "interview questions",
    "definition",
    "what is",
    "wikipedia"
]


# ============================================================
# EMAIL SETTINGS
# ============================================================

GENERIC_EMAIL_PREFIXES = {
    "info",
    "hello",
    "contact",
    "sales",
    "business",
    "support",
    "office",
    "team",
    "careers",
    "jobs",
    "hr",
    "partnerships",
    "partners",
    "enquiries",
    "inquiries"
}


BAD_EMAIL_FRAGMENTS = {
    "example.com",
    "sentry.io",
    "wixpress.com",
    "wordpress.org",
    "cloudflare.com",
    "schema.org"
}


HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/130 Safari/537.36"
}


# ============================================================
# SESSION STATE
# ============================================================

if "leads_df" not in st.session_state:
    st.session_state.leads_df = None

if "search_summary" not in st.session_state:
    st.session_state.search_summary = ""


# ============================================================
# BASIC FUNCTIONS
# ============================================================

def normalize(text):

    text = str(text or "").lower()

    text = re.sub(
        r"[^a-z0-9+#.\- ]",
        " ",
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def get_domain(url):

    try:

        domain = urlparse(
            str(url)
        ).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:

        return ""


def root_url(url):

    try:

        parsed = urlparse(
            str(url)
        )

        if (
            parsed.scheme in {"http", "https"}
            and parsed.netloc
        ):

            return (
                f"{parsed.scheme}://"
                f"{parsed.netloc}"
            )

        return ""

    except Exception:

        return ""


def canonical_url(url):

    try:

        parsed = urlparse(
            str(url)
        )

        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
        ):

            return ""

        clean = parsed._replace(
            query="",
            fragment=""
        )

        return urlunparse(
            clean
        ).rstrip("/")

    except Exception:

        return ""


def pretty_slug(text):

    text = re.sub(
        r"[-_]+",
        " ",
        str(text or "")
    )

    return " ".join(
        word.capitalize()
        for word in text.split()
    )


def is_aggregator(domain):

    domain = str(domain).lower()

    return any(
        item in domain
        for item in (
            AGGREGATORS
            | SOCIAL_DOMAINS
        )
    )


# ============================================================
# WEB SEARCH
# ============================================================

@st.cache_data(
    ttl=1200,
    show_spinner=False
)
def web_search(
    query,
    max_results=6,
    timelimit=None
):

    try:

        data = DDGS(
            timeout=10
        ).text(

            query,

            region="us-en",

            safesearch="moderate",

            timelimit=timelimit,

            max_results=int(
                max_results
            ),

            backend="auto"
        )

        return data or [], ""

    except Exception as first_error:

        # Retry without date filter.
        if timelimit:

            try:

                data = DDGS(
                    timeout=10
                ).text(

                    query,

                    region="us-en",

                    safesearch="moderate",

                    timelimit=None,

                    max_results=int(
                        max_results
                    ),

                    backend="auto"
                )

                return data or [], ""

            except Exception as second_error:

                return [], str(
                    second_error
                )

        return [], str(
            first_error
        )


# ============================================================
# QUERY GENERATOR
# ============================================================

def build_query(
    service,
    channel,
    location
):

    term = SERVICES[
        service
    ][0]

    location_text = (
        ""
        if location == "Worldwide"
        else location
    )


    templates = {

        "General Web":
            f'"{term}" hiring contract '
            f'consultant startup {location_text}',

        "Company Hiring":
            f'"{term}" "looking for" '
            f'hiring engineer {location_text}',

        "Contract / Consulting":
            f'"{term}" contract freelance '
            f'consultant outsourcing {location_text}',

        "Startup Opportunities":
            f'"{term}" startup hiring '
            f'prototype seeking {location_text}',

        "Product Development Projects":
            f'"{term}" "product development" '
            f'prototype project {location_text}',

        "Freelance Projects":
            f'"{term}" freelance project '
            f'contractor {location_text}',

        "Lever Jobs":
            f'site:jobs.lever.co '
            f'"{term}" {location_text}',

        "Greenhouse Jobs":
            f'site:greenhouse.io '
            f'"{term}" {location_text}',

        "Ashby Jobs":
            f'site:jobs.ashbyhq.com '
            f'"{term}" {location_text}',

        "Y Combinator":
            f'site:ycombinator.com '
            f'"{term}" hiring startup '
            f'{location_text}',

        "Wellfound":
            f'site:wellfound.com '
            f'"{term}" {location_text}',

        "RFP / RFQ / Tender":
            f'"{term}" RFP RFQ tender '
            f'engineering {location_text}'
    }


    return templates.get(
        channel,
        f'"{term}" {location_text}'
    ).strip()


# ============================================================
# MATCH SERVICES
# ============================================================

def matched_services(
    text,
    selected_services
):

    text = normalize(
        text
    )

    matches = []


    for service in selected_services:

        if any(
            normalize(term) in text
            for term in SERVICES[
                service
            ]
        ):

            matches.append(
                service
            )


    return matches


# ============================================================
# LEAD TYPE
# ============================================================

def detect_lead_type(text):

    text = normalize(
        text
    )


    if any(
        value in text
        for value in [
            "rfp",
            "rfq",
            "tender",
            "request for proposal"
        ]
    ):

        return "RFP / RFQ"


    if any(
        value in text
        for value in CONTRACT_TERMS
    ):

        return "Contract / Consulting"


    if any(
        value in text
        for value in [
            "outsource",
            "outsourcing",
            "vendor",
            "partner"
        ]
    ):

        return "Outsourcing / Partner"


    if any(
        value in text
        for value in [
            "hiring",
            "job",
            "career",
            "vacancy",
            "opening",
            "apply"
        ]
    ):

        return "Hiring"


    if (
        "prototype" in text
        or "product development" in text
    ):

        return "Product Development"


    return "Potential Opportunity"


# ============================================================
# LEAD SCORE
# ============================================================

def score_lead(
    title,
    body,
    url,
    selected_services
):

    text = normalize(
        f"{title} {body} {url}"
    )


    services = matched_services(
        text,
        selected_services
    )


    if services:

        score = 30

        score += min(
            max(
                len(services) - 1,
                0
            ) * 5,
            15
        )

    else:

        score = 0


    score += min(

        sum(
            1
            for value in HIGH_INTENT
            if normalize(value) in text
        ) * 7,

        25
    )


    if any(
        normalize(value) in text
        for value in CONTRACT_TERMS
    ):

        score += 10


    if any(
        normalize(value) in text
        for value in STARTUP_TERMS
    ):

        score += 8


    if any(
        normalize(value) in text
        for value in PRODUCT_TERMS
    ):

        score += 7


    if any(
        value in get_domain(url)
        for value in AGGREGATORS
    ):

        score += 5


    score -= (
        sum(
            1
            for value in NEGATIVE_TERMS
            if normalize(value) in text
        )
        * 10
    )


    return (
        max(
            0,
            min(
                int(score),
                100
            )
        ),
        services
    )


def quality_label(score):

    if score >= 75:
        return "Strong Lead"

    if score >= 55:
        return "Good Lead"

    if score >= 35:
        return "Possible Lead"

    return "Low Relevance"


# ============================================================
# COMPANY NAME
# ============================================================

def company_from_job_url(url):

    parsed = urlparse(
        str(url)
    )

    domain = get_domain(
        url
    )

    parts = [
        item
        for item
        in parsed.path.split("/")
        if item
    ]


    if (
        "lever.co" in domain
        and parts
    ):

        return pretty_slug(
            parts[0]
        )


    if (
        "greenhouse.io" in domain
        and parts
    ):

        for part in parts:

            if (
                part.lower()
                not in {
                    "embed",
                    "jobs",
                    "job",
                    "boards"
                }
                and not part.isdigit()
            ):

                return pretty_slug(
                    part
                )


    if (
        "ashbyhq.com" in domain
        and parts
    ):

        return pretty_slug(
            parts[0]
        )


    if (
        "ycombinator.com" in domain
        and "companies" in parts
    ):

        index = parts.index(
            "companies"
        )

        if index + 1 < len(parts):

            return pretty_slug(
                parts[
                    index + 1
                ]
            )


    return ""


def guess_company_name(
    title,
    url
):

    result = company_from_job_url(
        url
    )

    if result:
        return result


    title = str(
        title or ""
    ).strip()


    match = re.search(
        r"\b(?:at|@)\s+([^|–—]+)",
        title,
        re.I
    )


    if match:

        value = re.sub(
            r"\s+[-–—].*$",
            "",
            match.group(1)
        ).strip()


        if (
            len(value) > 2
            and len(value) < 80
        ):

            return value


    domain = get_domain(
        url
    )


    if (
        domain
        and not is_aggregator(
            domain
        )
    ):

        return pretty_slug(
            domain.split(".")[0]
        )


    for separator in [
        " | ",
        " — ",
        " – "
    ]:

        if separator in title:

            pieces = [
                item.strip()
                for item
                in title.split(
                    separator
                )
                if item.strip()
            ]


            for value in reversed(
                pieces
            ):

                if (
                    normalize(value)
                    not in {
                        "linkedin",
                        "indeed",
                        "wellfound",
                        "glassdoor",
                        "jobs",
                        "careers"
                    }
                    and len(value) < 80
                ):

                    return value


    return "Unknown"


# ============================================================
# FIND OFFICIAL WEBSITE
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def discover_website(
    company,
    source_url
):

    source_domain = get_domain(
        source_url
    )


    if (
        source_domain
        and not is_aggregator(
            source_domain
        )
    ):

        return root_url(
            source_url
        )


    if (
        not company
        or company == "Unknown"
    ):

        return ""


    results, _ = web_search(

        f'"{company}" official website',

        6,

        None
    )


    for item in results:

        url = item.get(
            "href",
            ""
        )

        domain = get_domain(
            url
        )


        if (
            domain
            and not is_aggregator(
                domain
            )
        ):

            return root_url(
                url
            )


    return ""


# ============================================================
# DOWNLOAD WEBSITE HTML
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def fetch_html(url):

    try:

        parsed = urlparse(
            str(url)
        )


        if (
            parsed.scheme
            not in {"http", "https"}
            or not parsed.netloc
        ):

            return "", ""


        response = requests.get(

            url,

            headers=HEADERS,

            timeout=8,

            allow_redirects=True
        )


        response.raise_for_status()


        content_type = (
            response.headers
            .get(
                "content-type",
                ""
            )
            .lower()
        )


        if (
            "text/html"
            not in content_type
        ):

            return "", response.url


        return (
            response.text[
                :2_000_000
            ],
            response.url
        )


    except Exception:

        return "", ""


# ============================================================
# EMAILS
# ============================================================

def valid_email(email):

    email = (
        str(email or "")
        .lower()
        .strip()
        .strip(
            ".,;:()[]{}<>"
        )
    )


    if not re.fullmatch(
        r"[a-z0-9._%+\-]+@"
        r"[a-z0-9.\-]+\."
        r"[a-z]{2,}",
        email
    ):

        return False


    if any(
        item in email
        for item
        in BAD_EMAIL_FRAGMENTS
    ):

        return False


    return True


def choose_email(
    emails,
    website_domain
):

    emails = sorted({

        email.lower()

        for email in emails

        if valid_email(
            email
        )
    })


    if not emails:

        return ""


    same_domain = [

        email

        for email in emails

        if (
            website_domain
            and email
            .split("@")[-1]
            .endswith(
                website_domain
            )
        )
    ]


    for pool in (
        same_domain,
        emails
    ):

        for email in pool:

            if (
                email
                .split("@")[0]
                in GENERIC_EMAIL_PREFIXES
            ):

                return email


        if pool:

            return pool[0]


    return ""


# ============================================================
# COMPANY DESCRIPTION
# ============================================================

def company_summary(soup):

    options = [

        {
            "name":
                "description"
        },

        {
            "property":
                "og:description"
        },

        {
            "name":
                "twitter:description"
        }
    ]


    for attributes in options:

        tag = soup.find(
            "meta",
            attrs=attributes
        )


        if (
            tag
            and tag.get(
                "content"
            )
        ):

            return re.sub(

                r"\s+",
                " ",
                tag.get(
                    "content"
                )

            ).strip()[:500]


    return ""


# ============================================================
# SOCIAL SCORE
# ============================================================

def social_score(data):

    weights = {

        "Official Website": 15,

        "Business Email": 20,

        "Public Phone": 10,

        "Contact Page": 10,

        "LinkedIn": 20,

        "X / Twitter": 5,

        "Instagram": 5,

        "Facebook": 3,

        "YouTube": 5,

        "GitHub": 7
    }


    score = sum(

        value

        for key, value
        in weights.items()

        if data.get(
            key
        )
    )


    return min(
        score,
        100
    )


# ============================================================
# ENRICH COMPANY
# ============================================================

def enrich_lead(row):

    website = discover_website(

        str(
            row.get(
                "Company",
                ""
            )
        ),

        str(
            row.get(
                "Opportunity URL",
                ""
            )
        )
    )


    data = {

        "Official Website":
            website,

        "Company Summary":
            "",

        "Business Email":
            "",

        "Public Phone":
            "",

        "Contact Page":
            "",

        "Careers Page":
            "",

        "LinkedIn":
            "",

        "X / Twitter":
            "",

        "Instagram":
            "",

        "Facebook":
            "",

        "YouTube":
            "",

        "GitHub":
            "",

        "Social Presence":
            0
    }


    if not website:

        return data


    html, final_url = fetch_html(
        website
    )


    if final_url:

        data[
            "Official Website"
        ] = (
            root_url(
                final_url
            )
            or website
        )


    if not html:

        return data


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    data[
        "Company Summary"
    ] = company_summary(
        soup
    )


    base = (
        data[
            "Official Website"
        ]
        or website
    )


    domain = get_domain(
        base
    )


    email_pattern = (
        r"\b[A-Za-z0-9._%+\-]+@"
        r"[A-Za-z0-9.\-]+\."
        r"[A-Za-z]{2,}\b"
    )


    emails = set(
        re.findall(
            email_pattern,
            html
        )
    )


    links = []

    phones = []


    for tag in soup.find_all(
        "a",
        href=True
    ):

        href = str(
            tag.get(
                "href",
                ""
            )
        ).strip()


        text = normalize(
            tag.get_text(
                " ",
                strip=True
            )
        )


        if href.lower().startswith(
            "mailto:"
        ):

            emails.add(

                href[7:]
                .split("?")[0]
                .strip()
            )

            continue


        if href.lower().startswith(
            "tel:"
        ):

            phone = (

                href[4:]
                .split("?")[0]
                .strip()
            )


            if (
                phone
                and phone
                not in phones
            ):

                phones.append(
                    phone
                )


            continue


        if href:

            links.append((

                text,

                urljoin(
                    base + "/",
                    href
                )
            ))


    data[
        "Business Email"
    ] = choose_email(
        emails,
        domain
    )


    data[
        "Public Phone"
    ] = (
        phones[0]
        if phones
        else ""
    )


    for text, link in links:

        lower = link.lower()


        if (
            "linkedin.com/company/"
            in lower
            and not data["LinkedIn"]
        ):

            data["LinkedIn"] = link


        elif (
            (
                "twitter.com/"
                in lower
                or "x.com/"
                in lower
            )
            and not data["X / Twitter"]
        ):

            data["X / Twitter"] = link


        elif (
            "instagram.com/"
            in lower
            and not data["Instagram"]
        ):

            data["Instagram"] = link


        elif (
            "facebook.com/"
            in lower
            and not data["Facebook"]
        ):

            data["Facebook"] = link


        elif (
            (
                "youtube.com/"
                in lower
                or "youtu.be/"
                in lower
            )
            and not data["YouTube"]
        ):

            data["YouTube"] = link


        elif (
            "github.com/"
            in lower
            and not data["GitHub"]
        ):

            data["GitHub"] = link


        if (
            not data["Contact Page"]
            and (
                "contact" in text
                or "/contact" in lower
            )
        ):

            data[
                "Contact Page"
            ] = link


        if (
            not data["Careers Page"]
            and (
                any(
                    item in text
                    for item in [
                        "career",
                        "careers",
                        "jobs",
                        "work with us"
                    ]
                )
                or any(
                    item in lower
                    for item in [
                        "/careers",
                        "/jobs"
                    ]
                )
            )
        ):

            data[
                "Careers Page"
            ] = link


    # Try public contact page for email.

    if (
        not data[
            "Business Email"
        ]
        and data[
            "Contact Page"
        ]
    ):

        contact_html, _ = fetch_html(
            data[
                "Contact Page"
            ]
        )


        if contact_html:

            contact_emails = set(
                re.findall(
                    email_pattern,
                    contact_html
                )
            )


            contact_soup = BeautifulSoup(
                contact_html,
                "html.parser"
            )


            for tag in contact_soup.find_all(
                "a",
                href=True
            ):

                href = str(
                    tag.get(
                        "href",
                        ""
                    )
                ).strip()


                if href.lower().startswith(
                    "mailto:"
                ):

                    contact_emails.add(

                        href[7:]
                        .split("?")[0]
                        .strip()
                    )


                elif (
                    href.lower().startswith(
                        "tel:"
                    )
                    and not data[
                        "Public Phone"
                    ]
                ):

                    data[
                        "Public Phone"
                    ] = (

                        href[4:]
                        .split("?")[0]
                        .strip()
                    )


            data[
                "Business Email"
            ] = choose_email(
                contact_emails,
                domain
            )


    data[
        "Social Presence"
    ] = int(
        social_score(
            data
        )
    )


    return data


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Lead Search"
)


selected_services = st.sidebar.multiselect(

    "Services",

    list(
        SERVICES
    ),

    default=[
        "Mechanical Design",
        "Product Development",
        "Robotics",
        "Mechatronics",
        "ROS 2",
        "Automation",
        "Drones / UAV",
        "CNC Design"
    ]
)


selected_channels = st.sidebar.multiselect(

    "Sources",

    CHANNELS,

    default=[
        "General Web",
        "Company Hiring",
        "Contract / Consulting",
        "Startup Opportunities"
    ]
)


location = st.sidebar.selectbox(

    "Location",

    LOCATIONS,

    index=1
)


period = st.sidebar.selectbox(

    "Search Period",

    list(
        TIME_MAP
    ),

    index=1
)


results_per_query = st.sidebar.slider(

    "Results per search",

    3,
    10,
    6
)


query_budget = st.sidebar.slider(

    "Maximum search queries",

    4,
    50,
    18
)


minimum_score = st.sidebar.slider(

    "Minimum lead score",

    0,
    100,
    25
)


st.sidebar.divider()

st.sidebar.subheader(
    "Company Enrichment"
)


enrich_enabled = st.sidebar.checkbox(

    "Find website, email, phone and socials",

    value=True
)


enrich_top_n = st.sidebar.slider(

    "Enrich top leads",

    1,
    20,
    5
)


# ============================================================
# SEARCH INPUT
# ============================================================

st.subheader(
    "What type of client are you looking for?"
)


custom_request = st.text_input(

    "Optional smart search",

    placeholder=(
        "Example: humanoid robotics startup looking for ROS 2, "
        "mechanical design, automation or prototype support"
    )
)


column1, column2 = st.columns(
    [5, 1]
)


with column1:

    run_search = st.button(

        "🔎 FIND BUSINESS LEADS",

        type="primary",

        use_container_width=True
    )


with column2:

    clear = st.button(

        "Clear",

        use_container_width=True
    )


if clear:

    st.session_state.leads_df = None

    st.session_state.search_summary = ""


# ============================================================
# RUN SEARCH
# ============================================================

if run_search:

    if not selected_services:

        st.error(
            "Select at least one service."
        )

        st.stop()


    if not selected_channels:

        st.error(
            "Select at least one source."
        )

        st.stop()


    queries = []


    # Custom query first.

    if custom_request.strip():

        query = custom_request.strip()


        if location != "Worldwide":

            query += (
                f" {location}"
            )


        queries.append(
            query
        )


    # Channel first gives better coverage
    # when query budget is limited.

    for channel in selected_channels:

        for service in selected_services:

            queries.append(

                build_query(
                    service,
                    channel,
                    location
                )
            )


    queries = list(
        dict.fromkeys(
            queries
        )
    )


    queries = queries[
        :int(query_budget)
    ]


    raw = []

    failures = 0


    progress = st.progress(
        0
    )


    status = st.empty()


    for index, query in enumerate(
        queries
    ):

        status.info(

            f"Searching "
            f"{index + 1}/"
            f"{len(queries)}: "
            f"{query}"
        )


        results, error = web_search(

            query,

            int(
                results_per_query
            ),

            TIME_MAP[
                period
            ]
        )


        if error:

            failures += 1


        for result in results:

            raw.append({

                "title":
                    result.get(
                        "title",
                        ""
                    ),

                "url":
                    result.get(
                        "href",
                        ""
                    ),

                "description":
                    result.get(
                        "body",
                        ""
                    ),

                "query":
                    query
            })


        progress.progress(

            int(
                (
                    (
                        index + 1
                    )
                    /
                    max(
                        len(queries),
                        1
                    )
                )
                * 100
            )
        )


        time.sleep(
            0.08
        )


    progress.empty()

    status.empty()


    # ========================================================
    # ANALYZE LEADS
    # ========================================================

    leads = []


    for result in raw:

        url = canonical_url(
            result["url"]
        )


        if not url:

            continue


        score, services = score_lead(

            result["title"],

            result[
                "description"
            ],

            url,

            selected_services
        )


        if score < int(
            minimum_score
        ):

            continue


        leads.append({

            "Lead Score":
                int(score),

            "Quality":
                quality_label(
                    score
                ),

            "Company":
                guess_company_name(
                    result["title"],
                    url
                ),

            "Opportunity":
                result["title"],

            "Lead Type":
                detect_lead_type(

                    f'{result["title"]} '
                    f'{result["description"]}'
                ),

            "Matched Services":
                ", ".join(
                    services
                ),

            "Description":
                result[
                    "description"
                ],

            "Opportunity URL":
                url,

            "Source Domain":
                get_domain(
                    url
                ),

            "Search Query":
                result[
                    "query"
                ]
        })


    if not leads:

        st.session_state.leads_df = None


        st.warning(
            "No useful leads passed the current threshold. "
            "Try Past Year or Any time, lower Minimum Lead Score, "
            "or search fewer services."
        )


        if failures:

            st.caption(
                f"{failures} search request(s) "
                f"were unavailable or rate-limited."
            )


    else:

        df = pd.DataFrame(
            leads
        )


        df = df.drop_duplicates(
            subset=[
                "Opportunity URL"
            ]
        )


        df = df.drop_duplicates(
            subset=[
                "Opportunity"
            ]
        )


        df = df.sort_values(

            "Lead Score",

            ascending=False

        ).reset_index(
            drop=True
        )


        # ====================================================
        # ENRICHMENT COLUMNS
        # ====================================================

        text_columns = [

            "Official Website",

            "Company Summary",

            "Business Email",

            "Public Phone",

            "Contact Page",

            "Careers Page",

            "LinkedIn",

            "X / Twitter",

            "Instagram",

            "Facebook",

            "YouTube",

            "GitHub"
        ]


        for column in text_columns:

            df[column] = pd.Series(

                [""] * len(df),

                dtype="object"
            )


        # Numeric column with an explicit dtype,
        # so text values are never mixed into it.

        df[
            "Social Presence"
        ] = pd.Series(

            [0] * len(df),

            dtype="int64"
        )


        # ====================================================
        # ENRICH TOP COMPANIES
        # ====================================================

        if enrich_enabled:

            count = min(

                int(
                    enrich_top_n
                ),

                len(df)
            )


            enrich_progress = st.progress(
                0
            )


            enrich_status = st.empty()


            for index in range(
                count
            ):

                enrich_status.info(

                    f"Researching company "
                    f"{index + 1}/"
                    f"{count}: "
                    f"{df.at[index, 'Company']}"
                )


                try:

                    data = enrich_lead(

                        df.iloc[
                            index
                        ].to_dict()
                    )


                    for key, value in data.items():

                        if key == "Social Presence":

                            df.at[
                                index,
                                key
                            ] = int(
                                value or 0
                            )


                        else:

                            df.at[
                                index,
                                key
                            ] = str(
                                value or ""
                            )


                except Exception:

                    # One unusual website should
                    # never crash the complete search.

                    pass


                enrich_progress.progress(

                    int(
                        (
                            (
                                index + 1
                            )
                            /
                            max(
                                count,
                                1
                            )
                        )
                        * 100
                    )
                )


            enrich_progress.empty()

            enrich_status.empty()


        # Final datatype safety.

        df[
            "Lead Score"
        ] = pd.to_numeric(

            df[
                "Lead Score"
            ],

            errors="coerce"

        ).fillna(
            0

        ).astype(
            int
        )


        df[
            "Social Presence"
        ] = pd.to_numeric(

            df[
                "Social Presence"
            ],

            errors="coerce"

        ).fillna(
            0

        ).astype(
            int
        )


        st.session_state.leads_df = df


        st.session_state.search_summary = (

            f"{len(raw)} raw results · "
            f"{len(df)} useful leads · "
            f"{failures} failed/rate-limited searches"
        )


# ============================================================
# DISPLAY RESULTS
# ============================================================

df = st.session_state.leads_df


if (
    isinstance(
        df,
        pd.DataFrame
    )
    and not df.empty
):

    st.success(
        st.session_state.search_summary
    )


    metric1, metric2, metric3, metric4, metric5 = st.columns(
        5
    )


    metric1.metric(
        "Useful Leads",
        len(df)
    )


    metric2.metric(

        "Strong Leads",

        int(
            (
                df[
                    "Lead Score"
                ]
                >= 75
            ).sum()
        )
    )


    metric3.metric(

        "Websites",

        int(

            df[
                "Official Website"
            ]
            .astype(str)
            .str.strip()
            .ne("")
            .sum()
        )
    )


    metric4.metric(

        "Business Emails",

        int(

            df[
                "Business Email"
            ]
            .astype(str)
            .str.strip()
            .ne("")
            .sum()
        )
    )


    metric5.metric(

        "LinkedIn",

        int(

            df[
                "LinkedIn"
            ]
            .astype(str)
            .str.strip()
            .ne("")
            .sum()
        )
    )


    # ========================================================
    # TABLE
    # ========================================================

    st.subheader(
        "Lead Database"
    )


    display_columns = [

        "Lead Score",

        "Quality",

        "Company",

        "Opportunity",

        "Lead Type",

        "Matched Services",

        "Official Website",

        "Business Email",

        "Public Phone",

        "LinkedIn",

        "X / Twitter",

        "Instagram",

        "Facebook",

        "YouTube",

        "GitHub",

        "Social Presence",

        "Opportunity URL",

        "Description"
    ]


    st.dataframe(

        df[
            display_columns
        ],

        hide_index=True,

        use_container_width=True,

        column_config={

            "Lead Score":
                st.column_config.ProgressColumn(

                    "Lead Score",

                    min_value=0,

                    max_value=100
                ),

            "Social Presence":
                st.column_config.ProgressColumn(

                    "Social Presence",

                    min_value=0,

                    max_value=100
                ),

            "Official Website":
                st.column_config.LinkColumn(
                    "Website"
                ),

            "LinkedIn":
                st.column_config.LinkColumn(
                    "LinkedIn"
                ),

            "X / Twitter":
                st.column_config.LinkColumn(
                    "X / Twitter"
                ),

            "Instagram":
                st.column_config.LinkColumn(
                    "Instagram"
                ),

            "Facebook":
                st.column_config.LinkColumn(
                    "Facebook"
                ),

            "YouTube":
                st.column_config.LinkColumn(
                    "YouTube"
                ),

            "GitHub":
                st.column_config.LinkColumn(
                    "GitHub"
                ),

            "Opportunity URL":
                st.column_config.LinkColumn(
                    "Opportunity"
                ),

            "Opportunity":
                st.column_config.TextColumn(
                    width="large"
                ),

            "Description":
                st.column_config.TextColumn(
                    width="large"
                )
        }
    )


    # ========================================================
    # TOP LEAD CARDS
    # ========================================================

    st.subheader(
        "Top Opportunities"
    )


    for _, lead in df.head(
        10
    ).iterrows():


        title = (

            f"{int(lead['Lead Score'])}/100 — "

            f"{lead['Company']} — "

            f"{lead['Opportunity']}"
        )


        with st.expander(
            title
        ):

            left, right = st.columns(
                [2, 1]
            )


            with left:

                st.write(
                    f"**Quality:** "
                    f"{lead['Quality']}"
                )


                st.write(
                    f"**Lead Type:** "
                    f"{lead['Lead Type']}"
                )


                st.write(
                    f"**Matched Services:** "
                    f"{lead['Matched Services'] or 'Related engineering opportunity'}"
                )


                if str(
                    lead[
                        "Company Summary"
                    ]
                ).strip():

                    st.write(
                        f"**Company Summary:** "
                        f"{lead['Company Summary']}"
                    )


                st.write(
                    f"**Public Business Email:** "
                    f"{lead['Business Email'] or 'Not found'}"
                )


                st.write(
                    f"**Public Phone:** "
                    f"{lead['Public Phone'] or 'Not found'}"
                )


                st.write(
                    f"**Opportunity:** "
                    f"{lead['Description']}"
                )


            with right:

                st.metric(

                    "Social Presence",

                    f"{int(lead['Social Presence'])}/100"
                )


                if str(
                    lead[
                        "Official Website"
                    ]
                ).strip():

                    st.link_button(

                        "🌐 Website",

                        lead[
                            "Official Website"
                        ]
                    )


                if str(
                    lead[
                        "Contact Page"
                    ]
                ).strip():

                    st.link_button(

                        "✉ Contact Page",

                        lead[
                            "Contact Page"
                        ]
                    )


                if str(
                    lead[
                        "LinkedIn"
                    ]
                ).strip():

                    st.link_button(

                        "LinkedIn",

                        lead[
                            "LinkedIn"
                        ]
                    )


                if str(
                    lead[
                        "GitHub"
                    ]
                ).strip():

                    st.link_button(

                        "GitHub",

                        lead[
                            "GitHub"
                        ]
                    )


                st.link_button(

                    "🔎 Original Opportunity",

                    lead[
                        "Opportunity URL"
                    ]
                )


    # ========================================================
    # DOWNLOAD CSV
    # ========================================================

    csv = df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    st.download_button(

        "⬇ Download Complete Lead Database",

        csv,

        "engineering_business_leads.csv",

        "text/csv",

        use_container_width=True
    )