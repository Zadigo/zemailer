import csv
import os
import re

from zemailer.core.file_opener import FileOpener
from zemailer.core.mixins.utils import UtilitiesMixin


class NameConstructor(FileOpener):
    """Subclass this class and build basic email patterns such 
    as `name.surname`.

    Send a `pattern` as a string, ex. `name.surname`, that
    will be used to construct the email. You can explicitly
    set the separator to be used or rely on the engine 
    presets for that.

    These presets are '.' or '-' or '_'.

    If provided, the `domain` will be appended, otherwise
    the structure will be returned as set by your pattern.

    The `particle` variable can be used to construct emails
    such as `nom.prenom-bba`. It must be a tuple or a list
    containing the string to append and the separator:

        (bba, -)
    """
    pattern = ''
    domain = ''
    separator = ''
    particle = ''

    def construct_pattern(self):
        # self.config['BASE_REGEX_PATTERNS']
        base_regex_patterns = {
            'with_separator': [
                # nom.prenom // prenom.nom
                # nom_prenom // prenom_nom
                # nom-prenom // prenom-nom
                r'^(?:(?:pre)?nom)(\S)(?:(?:pre)?nom)$',
                # n.prenom // p.nom
                # n-prenom // p-nom
                # n_prenom // p_nom
                r'^(?:n|p)(\S)(?:(?:pre)?nom)$'
            ],
            'without_separator': [
                # pnom
                # nprenom
                r'^(p|n)?((?:pre)?nom)$'
            ]
        }

        if self.pattern:
            if isinstance(self.pattern, str):
                if self.separator:
                    # If the user provided us
                    # with a separator, just use it
                    names = self.pattern.split(self.separator)

                else:
                    # Make sure there is a separator in there
                    # otherwise we have to use another logic
                    if '.' in self.pattern or '-' in self.pattern or \
                        '_' in self.pattern:
                        pattern_separator = ''
                        # We have to try and identify
                        # the type of separator used in the pattern
                        # TODO: Factorize this section
                        # into a function
                        for base_regex_pattern in base_regex_patterns['with_separator']:
                            pattern_separator = re.search(base_regex_pattern, self.pattern)
                            # Break on first match
                            if pattern_separator:
                                break
                        
                        # We can split the names once the separator has
                        # been correctly identified
                        # ex. ['nom', 'prenom']
                        separator_object = pattern_separator.group(1)
                        names = self.pattern.split(separator_object, 1)
                        
                        index_of_surname = names.index('nom')
                        index_of_name = names.index('prenom')

                        # We have to create a reusable
                        # canvas to prevent changing
                        # the names[...] data on each
                        # iteration
                        template_names = names.copy()

                        # Replace [name, surname] by the
                        # respective names in the file
                        # according to the index of name
                        # and surname in the array
                        # ex. [name, surname] => [pauline, lopez]
                        for items in self.csv_content:
                            template_names[index_of_surname] = items[0]
                            template_names[index_of_name] = items[1]
                            # Join both using the separator
                            final_pattern = separator_object.join(template_names)
                            # If a domain was provided,
                            # append it to the names
                            if self.domain:
                                items.append(self.append_domain(final_pattern))
                            else:
                                items.append(final_pattern)
                            # Reset the template
                            template_names = names

                        # Update & reinsert headers
                        self.headers.append('email')
                        self.csv_content.insert(0, self.headers)

                        return self.csv_content

                    else:
                        # TODO: Factorize this section
                        # into a function
                        for base_regex_pattern in base_regex_patterns['without_separator']:
                            captured_elements = re.search(base_regex_pattern, self.pattern)
                            # Break on first match
                            if captured_elements:
                                break
                        
                        # Get group(1) & group(2)
                        # ex. p, nom, n, prenom
                        first_captured_element = captured_elements.group(1)
                        second_captured_element = captured_elements.group(2)

                        truncated_name = truncated_surname = ''

                        for items in self.csv_content:
                            if first_captured_element == 'n':
                                # TODO: Factorize
                                truncated_surname = items[0][:1]
                            elif first_captured_element == 'p':
                                # TODO: Factorize
                                truncated_name = items[1][:1]

                            if second_captured_element == 'nom':
                                name_to_append = items[0]
                            elif second_captured_element == 'prenom':
                                name_to_append = items[1]

                            final_pattern = truncated_name + name_to_append or \
                                             truncated_surname + name_to_append
                                             
                            # If a domain was provided,
                            # append it to the names
                            if self.domain:
                                items.append(self.append_domain(final_pattern))
                            else:
                                items.append(final_pattern)

                        return self.csv_content                
            elif isinstance(self.pattern, (list, tuple)):
                # If we get a list or a tuple, this means
                # that we have to deal with multiple patterns
                # self.multiple_patterns(values=self.pattern)
                pass
            else:
                raise TypeError()
        else:
            # raise NoPatternError()
            raise Exception()

    def append_domain(self, name):
        """Append a domain such as `@example.fr`
        """
        return name + '@' + self.domain

    def search_separator(self, name, with_separator=True):
        """Get a regex match using the REGEX email
        engine. The `with_separator` parameter helps you match
        a pattern that has a separator or that has none
        """
        if with_separator:
            for base_regex_pattern in config['BASE_REGEX_PATTERNS']['with_separator']:
                captured_elements = re.search(base_regex_pattern, self.pattern)
                # Break on first match
                if captured_elements:
                    break
            return captured_elements.group(1)
        else:
            for base_regex_pattern in config['BASE_REGEX_PATTERNS']['without_separator']:
                captured_elements = re.search(base_regex_pattern, self.pattern)
                # Break on first match
                if captured_elements:
                    break

            # Get group(1) & group(2)
            # ex. p, nom; n, prenom...
            first_captured_element = captured_elements.group(1)
            second_captured_element = captured_elements.group(2)
            return first_captured_element, second_captured_element

    @classmethod
    def multiple_patterns(cls, **kwargs):
        # Construct a pattern
        # cls.construct_pattern(cls)
        # for name in kwargs['names']:
        #     # Search separator
        #     for pattern in kwargs['patterns']:
        #         cls.search_separator(cls, name)
        pass
