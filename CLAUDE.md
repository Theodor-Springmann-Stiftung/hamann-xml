# Best Practices Claude

## Content
- In this directory you'll find data for an online publications containing the letters of 18th century German philosopher Johann Georg Hamann. There are well above >1000 letters. The data is split up into multiple XML files, along domain lines:
    - `./briefe.xml`: Contains the letter fulltext.
    - `./meta.xml`: Contains metadata about the letters, such as the date of writing, the recipient, and the sender. ZH is data for cross referencing an earlier edition of the letters.
    - `./references.xml`: Contains reference data which is linked mostly in the metadata, for locations, people and definitions for terms used in descibing letter heritage data.
    - `./traditions.xml`: Contains data about the traditions of the letters, such as the edition they were published in, and the publisher, as well as - often times - additional information, other versions (or drafts) of the letters, and so on.
    - `./edits.xml`: Contains data about the editorial changes made to letters - often times comparing the edited text of sources to the original and restoring the original state as well as possible -, cross referencing edit-elements in the letter fulltext.
    - `./marginals.xml`: Contains commentary on letters, referencing them by ID, page- and line-numbers.

## Rules
- Rules for XML transformations:
    -
