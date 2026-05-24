import re
import traceback
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
BASE_URL       = "https://www.imdb.com"
LONG_WAIT      = 15
SHORT_WAIT     = 8
SEARCH_INPUT   = "input[placeholder='Search IMDb']"
RESULT_ITEM    = "li.ipc-metadata-list-summary-item"
RATING_STAR    = "span.ipc-rating-star--rating"
INCEPTION_URL  = "https://www.imdb.com/title/tt1375666/"
DICAPRIO_URL   = "https://www.imdb.com/name/nm0000138/"
TOP250_URL     = "https://www.imdb.com/chart/top/"
ADV_SEARCH_URL = (
    "https://www.imdb.com/search/title/"
    "?genres=action&release_date=2022-01-01,2022-12-31&sort=num_votes,desc"
)
class IMDBTestSuite:
    def __init__(self):
        print("=" * 54)
        print("       IMDB AUTOMATED TEST SUITE")
        print("=" * 54)
        print("\nInitialising WebDriver ...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(3)
        self.results = []
        self._run_start = datetime.now()
    def _wait(self, timeout=LONG_WAIT):
        return WebDriverWait(
            self.driver, timeout, poll_frequency=0.4,
            ignored_exceptions=[StaleElementReferenceException],
        )
    def _record(self, tc_id, description, passed, note=""):
        icon  = "OK" if passed else "FAIL"
        emoji = "  OK" if passed else "  XX"
        self.results.append((tc_id, description, passed, note))
        line = f"  {'OK ' if passed else 'XX '} {tc_id}: {description} - {'PASS' if passed else 'FAIL'}"
        if note:
            line += f"  [{note}]"
        emoji_line = line.replace("  OK ", "  [PASS] ").replace("  XX ", "  [FAIL] ")
        print(emoji_line)

    def _header(self, num, title):
        print(f"\n--- FLOW {num}: {title} ---")

    def _js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def _scroll_to(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", element
        )
    def run_all(self):
        try:
            self.flow_1_search_validation()
            self.flow_2_movie_detail()
            self.flow_3_top_rated_integrity()
            self.flow_4_actor_cross_navigation()
            self.flow_5_advanced_search_filtering()
        except Exception as exc:
            print(f"\nCRITICAL ERROR: {exc}")
            traceback.print_exc()
        finally:
            self._print_summary()
            self._write_report()
            self.driver.quit()
    # ==========================================================
    # FLOW 1 - Search Validation  (TC1, TC2, TC3)
    # ==========================================================
    def flow_1_search_validation(self):
        self._header(1, "Search Validation")
        try:
            self.driver.get(BASE_URL)
            box = self._wait().until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_INPUT))
            )
            box.clear()
            search_term = "Inception"
            box.send_keys(search_term)
            box.send_keys(Keys.ENTER)
            self._wait().until(EC.url_contains("find"))
            url = self.driver.current_url
            url_has_term = "inception" in url.lower() or "q=" in url.lower()

            body_el = self._wait(SHORT_WAIT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_mentions = search_term.lower() in body_el.text.lower()
            passed = url_has_term and page_mentions
            self._record(
                "TC1",
                "Search URL encodes query & results page confirms search term",
                passed,
                f"URL has term={url_has_term}, page mentions term={page_mentions}",
            )
        except Exception as exc:
            self._record("TC1",
                "Search URL encodes query & results page confirms search term",
                False, repr(exc)[:90])
        try:
            self.driver.get(BASE_URL)
            box = self._wait().until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_INPUT))
            )
            box.clear()
            box.send_keys("The Dark Knight")
            box.send_keys(Keys.ENTER)
            items = self._wait().until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, RESULT_ITEM))
            )
            first_text = items[0].text.lower()
            passed = "dark knight" in first_text and len(items) >= 3
            self._record("TC2", "Top search result title matches queried keyword",
                passed, f"First result: '{items[0].text[:50]}'")
        except Exception as exc:
            self._record("TC2", "Top search result title matches queried keyword",
                False, repr(exc)[:90])
        try:
            self.driver.get(BASE_URL)
            box = self._wait().until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SEARCH_INPUT))
            )
            box.clear()
            box.send_keys("@#$%^&*()")
            box.send_keys(Keys.ENTER)
            self._wait(SHORT_WAIT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            no_result_phrases = ["no results", "0 titles", "didn't find",
                                 "try another", "no matches"]
            graceful = any(p in body_text for p in no_result_phrases)
            items = self.driver.find_elements(By.CSS_SELECTOR, RESULT_ITEM)
            passed = graceful or len(items) == 0
            self._record("TC3",
                "Special-character search handled gracefully (no crash)", passed,
                "'no results' UI shown" if graceful else f"{len(items)} result(s) returned")
        except Exception as exc:
            self._record("TC3",
                "Special-character search handled gracefully (no crash)",
                False, repr(exc)[:90])
    # ==========================================================
    # FLOW 2 - Movie Detail Page Deep Validation  (TC4-TC7)
    # ==========================================================
    def flow_2_movie_detail(self):
        self._header(2, "Movie Detail Page Deep Validation")
        try:
            self.driver.get(INCEPTION_URL)
            self._wait().until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span[data-testid='hero__primary-text']")))
        except Exception as exc:
            print(f"  WARNING: Could not load Inception page: {exc}")
            for tc in ("TC4", "TC5", "TC6", "TC7"):
                self._record(tc, tc, False, "page failed to load")
            return
        try:
            runtime_el = self._wait(SHORT_WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "li[data-testid='title-techspec_runtime'] "
                    ".ipc-metadata-list-item__content-container,"
                    " [class*='TitleBlockMetaData'] li:last-child")))
            raw = runtime_el.text.strip()
            nums = re.findall(r"\d+", raw)
            total_mins = (int(nums[0])*60 + int(nums[1])) if len(nums) >= 2 \
                else int(nums[0]) if nums else 0
            passed = 30 <= total_mins <= 360
            self._record("TC4", "Runtime is present and within 30-360 minute range",
                passed, f"Parsed runtime: {total_mins} min  (raw='{raw}')")
        except Exception as exc:
            self._record("TC4", "Runtime is present and within 30-360 minute range",
                False, repr(exc)[:90])
        try:
            rating_el = self._wait(SHORT_WAIT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, RATING_STAR)))
            rating = float(rating_el.text.strip())
            passed = 0 < rating <= 10
            self._record("TC5", "IMDb rating is numeric and within valid 0-10 range",
                passed, f"Rating = {rating}")
        except Exception as exc:
            self._record("TC5", "IMDb rating is numeric and within valid 0-10 range",
                False, repr(exc)[:90])
        try:
            cast_links = self._wait().until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                    "[data-testid='title-cast-item'] a[href*='/name/nm']")))
            valid = [a for a in cast_links if a.get_attribute("href")]
            passed = len(valid) >= 5
            self._record("TC6", "Cast section has >=5 actors with valid profile links",
                passed, f"{len(valid)} valid cast link(s) found")
        except Exception as exc:
            self._record("TC6", "Cast section has >=5 actors with valid profile links",
                False, repr(exc)[:90])
        try:
            self._scroll_to(self.driver.find_element(By.TAG_NAME, "footer"))
            more_links = self._wait().until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                    "[data-testid='MoreLikeThis'] a[href*='/title/tt'],"
                    " section[class*='MoreLikeThis'] a[href*='/title/tt'],"
                    " [class*='more-like-this'] a[href*='/title/tt']")))
            valid = [a for a in more_links if a.get_attribute("href")]
            passed = len(valid) >= 3
            self._record("TC7", "'More Like This' section has >=3 clickable movie links",
                passed, f"{len(valid)} link(s) found")
        except Exception as exc:
            self._record("TC7", "'More Like This' section has >=3 clickable movie links",
                False, repr(exc)[:90])
    # ==========================================================
    # FLOW 3 - Top Rated List Integrity  (TC8, TC9, TC10)
    # ==========================================================
    def flow_3_top_rated_integrity(self):
        self._header(3, "Top Rated List Integrity")
        try:
            self.driver.get(TOP250_URL)
            movies = self._wait().until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, RESULT_ITEM)))
        except Exception as exc:
            print(f"  WARNING: Top 250 page failed to load: {exc}")
            for tc in ("TC8", "TC9", "TC10"):
                self._record(tc, tc, False, "page failed to load")
            return
        passed = len(movies) >= 25
        self._record("TC8", "Top 250 page renders >=25 movie entries",
            passed, f"{len(movies)} entries found")
        try:
            ratings = []
            for m in movies[:25]:
                try:
                    r_text = m.find_element(By.CSS_SELECTOR, RATING_STAR).text.strip()
                    ratings.append(float(r_text))
                except NoSuchElementException:
                    pass
            descending = all(ratings[i] >= ratings[i+1] for i in range(len(ratings)-1))
            passed = descending and len(ratings) >= 10
            self._record("TC9", "Top rated movies are in descending rating order", passed,
                f"Checked {len(ratings)} ratings; "
                f"highest={ratings[0] if ratings else 'N/A'}, "
                f"lowest={ratings[-1] if ratings else 'N/A'}")
        except Exception as exc:
            self._record("TC9", "Top rated movies are in descending rating order",
                False, repr(exc)[:90])
        try:
            hrefs = []
            for m in movies[:50]:
                try:
                    link = m.find_element(By.CSS_SELECTOR, "a[href*='/title/tt']")
                    hrefs.append(link.get_attribute("href").split("?")[0])
                except NoSuchElementException:
                    pass
            passed = len(hrefs) == len(set(hrefs)) and len(hrefs) > 0
            self._record("TC10", "All movie card URLs are unique within Top 250 list",
                passed, f"{len(hrefs)} URLs, {len(set(hrefs))} unique")
        except Exception as exc:
            self._record("TC10", "All movie card URLs are unique within Top 250 list",
                False, repr(exc)[:90])
    # ==========================================================
    # FLOW 4 - Actor Profile & Cross-Navigation  (TC11-TC13)
    # ==========================================================
    def flow_4_actor_cross_navigation(self):
        self._header(4, "Actor Profile & Cross-Navigation")
        try:
            self.driver.get(DICAPRIO_URL)
            self._wait().until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        except Exception as exc:
            print(f"  WARNING: Actor page failed to load: {exc}")
            for tc in ("TC11", "TC12", "TC13"):
                self._record(tc, tc, False, "page failed to load")
            return
        try:
            h1 = self._wait(SHORT_WAIT).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1")))
            name_text = h1.text.strip()
            passed = "DiCaprio" in name_text or "Leonardo" in name_text
            self._record("TC11", "Actor profile page displays the correct actor name",
                passed, f"h1 text = '{name_text}'")
        except Exception as exc:
            self._record("TC11", "Actor profile page displays the correct actor name",
                False, repr(exc)[:90])
        try:
            known_links = self._wait().until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                    "a[href*='/title/tt'][class*='ipc-primary-image-list-card__title'],"
                    " [data-testid='nm-flmg-known-for'] a[href*='/title/tt'],"
                    " section[class*='knownFor'] a[href*='/title/tt']")))
            valid = [a for a in known_links if a.get_attribute("href")]
            passed = len(valid) >= 3
            self._record("TC12", "'Known For' section has >=3 films with valid links",
                passed, f"{len(valid)} valid film link(s) found")
        except Exception as exc:
            self._record("TC12", "'Known For' section has >=3 films with valid links",
                False, repr(exc)[:90])
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/title/tt']")
            target_href = None
            for lnk in links:
                h = lnk.get_attribute("href") or ""
                if "/title/tt" in h and lnk.is_displayed():
                    target_href = h.split("?")[0]
                    break
            if not target_href:
                raise RuntimeError("No visible title link found on actor page")
            self.driver.get(target_href)
            movie_title_el = self._wait().until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span[data-testid='hero__primary-text']")))
            passed = bool(movie_title_el.text.strip())
            self._record("TC13",
                "Clicking filmography link navigates to a valid movie page",
                passed, f"Landed on: '{movie_title_el.text.strip()}'")
        except Exception as exc:
            self._record("TC13",
                "Clicking filmography link navigates to a valid movie page",
                False, repr(exc)[:90])
    # ==========================================================
    # FLOW 5 - Advanced Search Filtering  (TC14, TC15)
    # ==========================================================
    def flow_5_advanced_search_filtering(self):
        self._header(5, "Advanced Search Filtering (Genre + Year + Sort)")
        try:
            self.driver.get(ADV_SEARCH_URL)
            items = self._wait().until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, RESULT_ITEM)))
        except Exception as exc:
            print(f"  WARNING: Advanced search page failed: {exc}")
            self._record("TC14", "Advanced filter returns >=10 results",
                False, repr(exc)[:90])
            self._record("TC15", "Filtered results fall within specified year range",
                False, repr(exc)[:90])
            return
        passed = len(items) >= 10
        self._record("TC14", "Genre+year advanced filter returns >=10 results",
            passed, f"{len(items)} result(s) returned")
        try:
            year_pattern = re.compile(r"\b(?:19|20)\d{2}\b")
            out_of_range = []
            for item in items[:15]:
                text = item.text
                years_found = [int(y) for y in year_pattern.findall(text)]
                for y in years_found:
                    if not (2022 <= y <= 2022):
                        out_of_range.append(y)
                        break
            passed = len(out_of_range) == 0
            self._record("TC15",
                "All filtered results fall within the specified year range (2022)",
                passed,
                "All match" if passed
                else f"Out-of-range years found: {out_of_range[:5]}")
        except Exception as exc:
            self._record("TC15",
                "All filtered results fall within the specified year range (2022)",
                False, repr(exc)[:90])
    def _print_summary(self):
        passed_count = sum(1 for _, _, p, _ in self.results if p)
        total = len(self.results)
        print("\n" + "=" * 54)
        print("               TEST SUMMARY")
        print("=" * 54)
        print(f"\n  Total Test Cases Executed: {total}/15\n")
        for tc_id, description, passed, _ in self.results:
            icon = "[OK]" if passed else "[XX]"
            print(f"  {icon} {tc_id}:\t{description}")
        pct = (passed_count / total * 100) if total else 0
        print(f"\n  Success Rate: {passed_count}/{total} Passed  ({pct:.0f}%)")
        print("=" * 54 + "\n")
    def _write_report(self):
        run_end  = datetime.now()
        duration = run_end - self._run_start
        passed   = [r for r in self.results if r[2]]
        failed   = [r for r in self.results if not r[2]]
        pct      = (len(passed) / len(self.results) * 100) if self.results else 0
        flow_map = {
            "TC1":  "Flow 1 - Search Validation",
            "TC2":  "Flow 1 - Search Validation",
            "TC3":  "Flow 1 - Search Validation",
            "TC4":  "Flow 2 - Movie Detail Page Deep Validation",
            "TC5":  "Flow 2 - Movie Detail Page Deep Validation",
            "TC6":  "Flow 2 - Movie Detail Page Deep Validation",
            "TC7":  "Flow 2 - Movie Detail Page Deep Validation",
            "TC8":  "Flow 3 - Top Rated List Integrity",
            "TC9":  "Flow 3 - Top Rated List Integrity",
            "TC10": "Flow 3 - Top Rated List Integrity",
            "TC11": "Flow 4 - Actor Profile & Cross-Navigation",
            "TC12": "Flow 4 - Actor Profile & Cross-Navigation",
            "TC13": "Flow 4 - Actor Profile & Cross-Navigation",
            "TC14": "Flow 5 - Advanced Search Filtering",
            "TC15": "Flow 5 - Advanced Search Filtering",
        }
        lines = []
        def L(text=""):
            lines.append(text)

        L("=" * 64)
        L("         IMDB SELENIUM AUTOMATED TEST REPORT")
        L("=" * 64)
        L()
        L("  RUN METADATA")
        L("  " + "-" * 42)
        L(f"  Start Time   : {self._run_start.strftime('%Y-%m-%d  %H:%M:%S')}")
        L(f"  End Time     : {run_end.strftime('%Y-%m-%d  %H:%M:%S')}")
        L(f"  Duration     : {str(duration).split('.')[0]}")
        L(f"  Browser      : Google Chrome (ChromeDriver)")
        L(f"  Target Site  : https://www.imdb.com")
        L(f"  Total TCs    : {len(self.results)} / 15")
        L(f"  Passed       : {len(passed)}")
        L(f"  Failed       : {len(failed)}")
        L(f"  Pass Rate    : {pct:.1f}%")
        L()
        flows_seen = {}
        for tc_id, desc, p, note in self.results:
            flow = flow_map.get(tc_id, "Unknown Flow")
            flows_seen.setdefault(flow, []).append((tc_id, desc, p, note))

        L("=" * 64)
        L("  FLOW-BY-FLOW BREAKDOWN")
        L("=" * 64)
        for flow_name, tcs in flows_seen.items():
            fp = sum(1 for _, _, p, _ in tcs if p)
            L()
            L(f"  > {flow_name}")
            L(f"    Result : {fp}/{len(tcs)} passed")
            for tc_id, desc, p, note in tcs:
                status = "PASS" if p else "FAIL"
                mark   = "[OK]" if p else "[XX]"
                L(f"      {mark} {tc_id:5s} {status:4s}  {desc}")
                if note:
                    L(f"      {'':6}          Note: {note}")
        L()
        L("=" * 64)
        L("  FULL TEST CASE LOG")
        L("=" * 64)
        L()
        L(f"  {'TC ID':<6}  {'STATUS':<6}  {'DESCRIPTION'}")
        L("  " + "-" * 60)
        for tc_id, desc, p, note in self.results:
            status = "PASS" if p else "FAIL"
            L(f"  {tc_id:<6}  {status:<6}  {desc}")
            if note:
                L(f"  {'':6}  {'':6}  -> {note}")
        if failed:
            L()
            L("=" * 64)
            L("  FAILED TEST CASES - ACTION REQUIRED")
            L("=" * 64)
            for tc_id, desc, _, note in failed:
                L()
                L(f"  FAIL {tc_id}: {desc}")
                L(f"       Flow   : {flow_map.get(tc_id, 'N/A')}")
                L(f"       Note   : {note}")
                L(f"       Action : Review selector / timing for {tc_id}")
        else:
            L()
            L("  All test cases passed - no failures to report.")
        L()
        L("=" * 64)
        L("  COVERAGE SUMMARY")
        L("=" * 64)
        L()
        L("  Web Elements Exercised:")
        L("    * Text input fields    (search box, keyword entry)")
        L("    * Hyperlinks           (cast, filmography, movie cards)")
        L("    * Parameterised URLs   (advanced search query string filters)")
        L("    * Rendered list items  (Top 250, search results, cast, known-for)")
        L("    * Heading elements     (h1, hero primary text span)")
        L("    * Footer / scroll      (More Like This section)")
        L()
        L("  Wait Strategy:")
        L("    * Implicit wait  :  3 s  (WebDriver baseline)")
        L("    * Explicit wait  : 15 s  (page transitions - LONG_WAIT)")
        L("    * Short wait     :  8 s  (element appearance - SHORT_WAIT)")
        L("    * Poll frequency :  0.4 s")
        L("    * StaleElementReferenceException ignored in all waits")
        L("    * Zero time.sleep() calls in production code")
        L()
        L("  Error Handling:")
        L("    * Every TC wrapped in independent try/except block")
        L("    * Flow-level guard prevents one flow's crash cascading")
        L("    * Critical top-level try/except in run_all()")
        L("    * Failed TCs record a note and continue - suite never aborts")
        L()
        L("=" * 64)
        L(f"  Report generated : {run_end.strftime('%Y-%m-%d %H:%M:%S')}")
        L("=" * 64)
        report_path = Path("imdb_test_report.txt")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Report saved -> {report_path.resolve()}\n")
if __name__ == "__main__":
    suite = IMDBTestSuite()
    suite.run_all()