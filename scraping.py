from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re
import requests


class Scraper:
    """
    A base web scraping class that provides utilities to extract HTML elements
    from a BeautifulSoup-parsed document created during initialization.
    """

    @staticmethod
    def css_extract_text(which='first', join_character='\n'):
        """
        Decorator to extract text content from HTML elements using a CSS selector.

        Args:
            which (str): Specifies which element(s) to return. Options are:
                - 'first': Return the first matching element's text (default).
                - 'last': Return the last matching element's text.
                - 'all': Return all matching elements' text.
            as_string (bool): If `which='all'`, determines the return format:
                - True: Return a single string with all texts joined by newline.
                - False: Return a list of individual text strings.

        Returns:
            property: A property that extracts and returns the selected text content
            from the HTML using the selector returned by the decorated method.
        """
        if which not in ['first', 'last', 'all']:
            raise ValueError('Invalid argument: "which" must be one of "first", "last", or "all".')

        def extract_content(func):
            @property
            def extract(self):
                """
                Extracts the text content based on the provided CSS selector and options.

                Returns:
                    str | list[str] | None: Extracted text(s) from the HTML content.
                """
                selector = func(self)
                tags_selected = self.soup.select(selector)
                if not tags_selected:
                    return None
                if which == 'first':
                    return tags_selected[0].text
                elif which == 'last':
                    return tags_selected[-1].text
                elif which == 'all':
                    return join_character.join([tag.text for tag in tags_selected])

            return extract

        return extract_content


    @staticmethod
    def re_extract_text(group=1, flags=0, all_matches=False, outer_tag=None, join_character='\n'):
        """
        Decorator to extract text content from the HTML using a regular expression.

        Args:
            group (int): The regex group number to extract (default is 1).
            flags (int): Optional regex flags (e.g., re.IGNORECASE).
            all_matches (bool): If True, returns all matches instead of just the first.
            as_string (bool): If multiple matches, return them as a single string
                              joined by newline (if True) or as a list (if False).

        Returns:
            property: A property that extracts text(s) from the HTML content using regex.
        """

        def extract_content(func):
            @property
            def extract(self):
                """
                Extracts the desired content using the regex pattern provided by the decorated method.

                Returns:
                    str | list[str] | None: The extracted text(s) from the HTML content.
                """
                pattern = func(self)
                if outer_tag is not None:
                    html_text = self.soup.select(outer_tag)[0].text
                else:
                    html_text = self.soup.text

                matches = re.findall(pattern, html_text, flags)

                if not matches:
                    return None

                if not all_matches:
                    return matches[group - 1] if isinstance(matches[0], tuple) else matches[0]

                return join_character.join(m[group - 1] if isinstance(m, tuple) else m for m in matches)

            return extract
        return extract_content

    @staticmethod
    def tag_matches_text(tag_name='p', multiple=False):
        """
        Decorator factory that returns a property-decorator for methods which return a regex pattern.
        This decorator searches the BeautifulSoup `soup` object for elements that match the given tag name
        and whose text content matches the regex pattern returned by the decorated method.

        Parameters:
        ----------
        tag_name : str, optional
            The name of the HTML tag to search for. Defaults to 'p'.
        multiple : bool, optional
            If True, returns a list of all matching tags. If False, returns only the first matching tag. Defaults to False.

        Returns:
        -------
        decorator : function
            A decorator that wraps a method and returns a property with the matched tag(s) from the HTML.
        """

        def decorator(method):
            """
            The actual decorator that wraps the method with a property.
            The method must return a string pattern to compile as a regular expression.
            """

            @property
            def wrapped(self):
                """
                Property method that performs the regex match against the text of HTML elements
                using BeautifulSoup's `find` or `select` method, depending on the `multiple` flag.
                """
                # Compile the regex pattern returned by the decorated method
                pattern = re.compile(method(self))

                if not multiple:
                    # Return the first matching tag element
                    matched_tag = self.soup.find(tag_name, string=pattern)
                    return matched_tag
                else:
                    # Return all matching tag elements
                    matched_tags = self.soup.select(tag_name, string=pattern)
                    return matched_tags

            return wrapped

        return decorator


    def __init__(self, url):
        self.url = url
        self.req = requests.get(url)
        self.req_ok = (self.req.status_code == 200)
        if self.req_ok:
            self.soup = BeautifulSoup(self.req.content, 'html.parser')


    def _scrape_sibling(self, re_pattern, tag_type='p'):
        """
        Find the html element which text contains a string with the given pattern. If
        the file exists in the page, returns the content of its sibling tag, otherwise
        return None.
        :param re_pattern: pattern to find the tag.
        :param tag_type: type of the tag to find.
        :return: text of the sibling tag found, or None if not found.
        """
        tag_element = self.soup.find(tag_type, string=re.compile(re_pattern))
        if not tag_element:
            return None
        sibling_element = tag_element.find_next_sibling() or tag_element.find_previous_sibling()
        if sibling_element:
            return sibling_element.text
        return None

    def __getattr__(self, attr):
        return None

    def _scrape_css_selector(self,  css_selector, found_many='first', as_string=True, **kwargs):
        """
        Given a valid CSS selector, find the first element which matches the selector and
        returns its content (as a string, or as a list of tags matched).

        :param css_selector: string containing the CSS selector to find.
        :param found_many: action to perform if many tags are found to match the CSS selector.
        :param as_string: weather the method will return the tag or its tag.
        :param kwargs: additional parameters to pass to the CSS selector method.
        :return: all_tags (as a string if as_string is True, or a list of tags if as_string is False).
        """
        if not found_many in ['first', 'last', 'all']:
            raise ValueError('found many most be in ["first", "last", "all"], but {} passed'.format(found_many))
        all_tags = self.soup.select(css_selector, **kwargs)
        if not all_tags:
            return None
        if as_string:
            match found_many:
                case 'first':
                    return all_tags[0].text
                case 'last':
                    return all_tags[-1].text
                case 'all':
                    return ''.join(all_tags)
        else:
            match found_many:
                case 'first':
                    return all_tags[0]
                case 'last':
                    return all_tags[-1]
                case 'all':
                    return all_tags


class PageIterator(ABC):
    """
    This abstract base class provides a foundation for scraping paginated lists of items from webpages.
    Concrete subclasses must implement the iteration protocol (through the __iter__ magic method),
    yielding a PlatformWebScraper instance for each page of results.
    This PlatformPageScraper instance should be capable of scraping the individual items on that specific
    page.
    """
    def __iter__(self):
        self.next_iteration = 0
        return self

    @abstractmethod
    def __next__(self):
        """
        All classes must implement this method to iterate over the pages
        of the current website to extract the pages with the list of car
        items.

        :return: PlatformWebScraper instance
        """
        pass


if __name__ == '__main__':
    pass

