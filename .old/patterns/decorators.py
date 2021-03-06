from app.mixins.utils import UtilitiesMixin

utilities = UtilitiesMixin()

def construct_emails(func):
    """A decorator function that can be used to construct
    a list of emails from  a list of names.

    Example
    -------

    Suppose you have a function that returns a list or a tuple
    and from these returned values (which are names) you wish
    to construct a list of emails:

        @construct_emails
        def test_function():
            names = [Eugenie Bouchard, Maria Sharapova]
            return names

        constructor(., gmail.com)

        You can pass one domain or multiple domains.

        In which case, an email will be constructed for each
        domains that were provided.

        You will then get a list of constructed emails using the
        separator and the domain that you provided:

        [eugenie.bouchard@google.com, maria.sharapova@google.com]

        Finally, if you wish to reverse the position of the name and
        the surname, use the `reverse = True` parameter.

    This decorator is an alternative to utilizing the email construction 
    classes.
    """
    def constructor(separator, domains=['gmail.com'], reverse_names=False):
        names = func()
        if not isinstance(names, (list, tuple)):
            raise TypeError("Names should be a list"
                "or a tuple of names. Received '%s'" % type(names))

        new_names = []
        new_name = ''

        for name in names:
            # Take out all the accents, spaces and
            # lowercase the names
            new_name = utilities.flatten_name(name)
            splitted_name = new_name.split(' ')

            # In case we want bouchard.eugenie
            # instead of eugenie.bouchard
            # if reverse_names:
            #     splitted_name.reverse()

            # Create the new name using the separator
            constructed_name = separator.join(splitted_name)

            for domain in domains:
                # TODO: Maybe yield the names as a generator
                # as opposed to the list below
                new_names.append(constructed_name + '@' + domain)

        return new_names
    return constructor
