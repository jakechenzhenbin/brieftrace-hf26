# BriefTrace review

Fictional example; no real customer.

English prototype. Semantic retrieval can miss negation, amounts and obligations. Scores are similarity, not confidence or a scope verdict. No price, contract or client message is generated automatically.

## R01: Could the contact form forward enquiries to our inbox?
Needs review
Related wording found, but its scope is unclear. Human review is needed.

- B02 (included; similarity 0.4303): [IN] A contact form that sends customer enquiries to the bakery email address.
- B04 (excluded; similarity 0.0953): [OUT] E-commerce, checkout and online payments.
- B05 (excluded; similarity 0.0452): [OUT] Extra languages and translation of website pages.

## R02: Can we accept credit cards for cake preorders?
Boundary to check
An exclusion or limit appears among the close matches. Check the quoted evidence.

- B04 (excluded; similarity 0.3494): [OUT] E-commerce, checkout and online payments.
- B02 (included; similarity 0.2231): [IN] A contact form that sends customer enquiries to the bakery email address.
- B01 (included; similarity 0.1336): [IN] One English landing page for a neighbourhood bakery, for desktop and mobile.

## R03: Please add a French version of the website.
Boundary to check
An exclusion or limit appears among the close matches. Check the quoted evidence.

- B05 (excluded; similarity 0.5283): [OUT] Extra languages and translation of website pages.
- B01 (included; similarity 0.3484): [IN] One English landing page for a neighbourhood bakery, for desktop and mobile.
- B02 (included; similarity 0.1365): [IN] A contact form that sends customer enquiries to the bakery email address.

## R04: Can you deliver a 3D animation of our new cake?
Needs review
No close wording found. Ask for clarification before agreeing.

- B02 (included; similarity 0.2789): [IN] A contact form that sends customer enquiries to the bakery email address.
- B01 (included; similarity 0.2444): [IN] One English landing page for a neighbourhood bakery, for desktop and mobile.
- B03 (limit; similarity 0.228): [LIMIT] Two rounds of visual design revisions.

Model: all-MiniLM-L6-v2 / local CPU
Revision: 1110a243fdf4706b3f48f1d95db1a4f5529b4d41

Prepared locally. No message sent.