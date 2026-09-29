"""Physics and Maths Tutor integration, independent of the user interface."""
from html.parser import HTMLParser
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen
import re
from .config import CONFIG, get_logger

LOGGER = get_logger(__name__)
PMT_SUBJECTS = {"Maths":"maths", "Further Maths":"further-maths", "Biology":"biology", "Chemistry":"chemistry", "Physics":"physics", "Economics":"economics", "Geography":"geography", "English Literature":"english-literature", "Psychology":"psychology", "Computer Science":"computer-science"}
PMT_SUBJECT_PATHS = {"maths":"maths/a-level", "further-maths":"maths/a-level/further-maths", "biology":"biology/a-level", "chemistry":"chemistry/a-level", "physics":"physics/a-level", "economics":"economics-revision", "geography":"geography-revision", "english-literature":"english-literature-revision", "psychology":"psychology-revision"}
PMT_BOARD_PATHS = {"AQA":"aqa", "Edexcel":"edexcel", "OCR":"ocr", "OCR A":"ocr-a", "OCR B":"ocr-b", "CIE":"cie", "WJEC":"wjec", "Eduqas":"eduqas"}
PMT_BOARDS = tuple(PMT_BOARD_PATHS)


def make_id(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def pmt_page_url(subject: str, board: str) -> str | None:
    subject_id, board = make_id(subject), board.strip()
    if subject_id == "computer-science":
        suffix = {"AQA":"a-level-aqa", "OCR":"a-level-ocr"}.get(board)
        return f"{CONFIG.pmt_base_url}/computer-science-revision/{suffix}/" if suffix else None
    subject_path, board_path = PMT_SUBJECT_PATHS.get(subject_id), PMT_BOARD_PATHS.get(board)
    if not subject_path or not board_path:
        return None
    suffix = board_path if subject_id in {"maths", "further-maths", "biology", "chemistry", "physics"} else f"a-level-{board_path}"
    return f"{CONFIG.pmt_base_url}/{subject_path}/{suffix}/"


class TopicParser(HTMLParser):
    def __init__(self, page_url: str) -> None:
        super().__init__(); self.page_url = page_url; self.links = []; self.href = None; self.text = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a" and self.href is None: self.href = dict(attrs).get("href"); self.text = []
    def handle_data(self, data: str) -> None:
        if self.href is not None: self.text.append(data)
    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self.href: return
        name = " ".join("".join(self.text).split()); full, _ = urldefrag(urljoin(self.page_url, self.href)); page, link = urlparse(self.page_url), urlparse(full)
        inside = link.path.rstrip("/") == page.path.rstrip("/") or link.path.startswith(page.path.rstrip("/") + "/")
        ignored = {"", "home", "revision", "past papers", "mark schemes", "notes"}
        if link.netloc == page.netloc and inside and name and name.casefold() not in ignored and not link.path.lower().endswith((".pdf", ".doc", ".docx")) and not any(x["url"] == full for x in self.links): self.links.append({"name": name, "notes": "", "url": full})
        self.href, self.text = None, []


def fetch_pmt_topics(subject: str, board: str) -> tuple[list[dict[str, str]], str]:
    url = pmt_page_url(subject, board)
    if not url: raise ValueError("Unsupported subject and exam-board combination.")
    last_error = None
    for attempt in range(CONFIG.max_retries):
        try:
            request = Request(url, headers={"User-Agent": "StudyPlanner/1.0"})
            with urlopen(request, timeout=CONFIG.request_timeout) as response:
                parser = TopicParser(url); parser.feed(response.read().decode(response.headers.get_content_charset() or "utf-8", errors="ignore"))
            if not parser.links: raise ValueError("No topic links were found.")
            return parser.links, url
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            last_error = error; LOGGER.warning("PMT request attempt %s failed: %s", attempt + 1, error)
            if attempt + 1 < CONFIG.max_retries: sleep(2 ** attempt)
    raise last_error or RuntimeError("PMT request failed")
