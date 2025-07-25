# Best Practices Claude

## Content
- In this directory you'll find data for an online publications containing the letters of 18th century German philosopher Johann Georg Hamann. There are well above >1000 letters. The data is split up into multiple XML files, along domain lines:
    - `./briefe.xml`: Contains the letter fulltext.
    - `./meta.xml`: Contains metadata about the letters, such as the date of writing, the recipient, and the sender. ZH is data for cross referencing an earlier edition of the letters.
    - `./references.xml`: Contains reference data which is linked mostly in the metadata, for locations, people and definitions for terms used in descibing letter heritage data.
    - `./traditions.xml`: Contains data about the traditions of the letters, such as the edition they were published in, and the publisher, as well as - often times - additional information, other versions (or drafts) of the letters, and so on.
    - `./edits.xml`: Contains data about the editorial changes made to letters - often times comparing the edited text of sources to the original and restoring the original state as well as possible -, cross referencing edit-elements in the letter fulltext.
    - `./Marginal-Kommentar.xml`: Contains commentary on letters, referencing them by ID, page- and line-numbers.
    - `./Bibel-Kommentar.xml`, `forschung.xml`, `Register-Kommentar.xml`: Contains a glossary of referenced bible verses, a list of research titles, and a register of terms, but mostly persons and works referenced and linked in the letter commentary.

## Rules
- What to do when an XML transformation is requested:
    - Before transforming the XML, give a few examples of how you understand the users request and how you would transform the XML. Try to use a diverse set of test cases, from the start, middle and end of a file.
    - After giving examples, you'll likely will need to write a python script to transform the XML. Use the `lxml.etree` library to parse the XML in python and transform it. It is important that this library and no other library is used! If text should be transformed, try to find the right place in XML witth said library, then you are allowed to use regex to transform text.
    - Before running the script, make sure to test it on a subset of the XML data, with a variety of test cases, from a variety of places from the target file, so the user can see if it works as expected. Alternatively, generate test data to test the transformations against. You are only allowed to do those transformations the user asked for, and nothing else.
    - All XML comments must be preserved. All other data must be preserved. You should use the ptyhon library to format the output XML, if the file is meta.xml or references.xml. All other files shold be formatted the way they were, so look at the formatting to get an impression.
    - After running all the transformations on the test data successfully show (and preserve) the test data, for user review. Then, ask the user to confirm the transformation on the real production data. If the user agreesm, run the script on the production data. Replace the original files, so the user can run git diff to see the changes made.
    - Save all generated scripts in the `scripts/` directory with the current date and a meaningful name, so they can be reused later.
