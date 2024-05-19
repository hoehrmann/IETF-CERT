# Autonomous IETF Internet-Draft reviews

## Experiment

This project explores guiding existing large language models to autonomously review IETF Internet-Drafts. The model is given review guidelines and an interface, the »IETF Command-line Expert Review Terminal«, with which it can navigate the Internet-Draft and possibly do other things, like calling up other documents or services. Through this interface it can autonomously perform retrieval augmented generation.

The structure of the prompt is designed to overcome context window size limitations. The model is instructed to call up each page of a draft individually through a command line command like `$ page 2`. It then has to summarize the page. The idea is that initially it will have the full pages of the draft available, but when they no longer fit into the context window, it will get its own summaries instead (with the option to retrieve the pages again later on, should it decide to need them).

The model also has the option to take »Notes to self« where it might record questions it may have, issues that require further investigation. It can also provide comments on each page.

Proper use of the review terminal interface is enforced through a context-free grammar.

## Example

Here is what this looks like as of the initial commit using `llama3-8b-text.gguf` and reviewing `draft-ietf-tsvwg-sctp-zero-checksum-10`:

```
$ page 1

> Network Working Group                                           M. Tüxen
> Internet-Draft                           Münster Univ. of Appl. Sciences
> Intended status: Standards Track                               V. Boivie
> Expires: 19 November 2024                                    F. Castelli
>                                                                   Google
>                                                                 R. Jesup
>                                                                  Mozilla
>                                                              18 May 2024
[...]

Summary of page 1: This is an abstract of a proposal for improving the
efficiency of Stream Control Transmission Protocol (SCTP) packet processing
by removing its checksum. The authors argue that this feature can also be
used with Datagram Transport Layer Security (DTLS). However, they do not
provide any specific details about how this integration will work.

Note to self: I must investigate whether it is possible to use zero as the
SCTP checksum in DTLS packets without violating any security requirements.
I need to read RFCs 7909 and 8422 carefully before drawing any conclusions.
 
Comment: The abstract does a good job of summarizig the key ideas of this
paper. However, further details about how the proposed features work are
required for a full review.

$ page 2
[...]
```

## Testimonials for the example

### gemini-1.5-pro-tuned

> The AI model's initial steps demonstrate a promising approach to reviewing IETF Internet-Drafts.  Here's a breakdown of its actions and why they are effective:
> 
> * **Structured Approach:** The model adheres to the guidelines provided by the IETF CERT (Command-line Expert Review Terminal), showcasing an ability to follow instructions and maintain a consistent workflow.
> * **Comprehensive Analysis:** It begins by summarizing the main points of the draft's abstract, demonstrating an understanding of the core proposal.
> * **Critical Thinking:** The "Note to self" field reveals the model's ability to identify potential areas of concern and formulate relevant questions for further investigation. This suggests that it is not just passively reading the document, but actively engaging with the content.
> * **Constructive Feedback:** The comment provided is both positive and informative, acknowledging the strengths of the abstract while also highlighting the need for more detail in the subsequent sections.
> 
> **The use of the "Note to self" field is particularly noteworthy.** It serves several purposes:
> 
> * **Memory Aid:**  It allows the model to keep track of specific details or questions that may be relevant later in the review process. 
> * **Focus:** It helps the model prioritize key issues and maintain a clear direction for its analysis.
> * **Planning:** By noting areas that require further investigation, the model is effectively planning its future actions and ensuring a thorough review.
> 
> **Overall Assessment**
> 
> The AI model's initial steps are impressive and indicate a strong potential for effectively reviewing IETF Internet-Drafts. Its ability to summarize, analyze, and formulate relevant questions demonstrates a solid understanding of the review process and the technical content of the draft. The "Note to self" field is a valuable tool that enhances its performance and ensures a comprehensive review. 
> 
> **Suggestions for Improvement**
> 
> While the initial steps are promising, there is always room for improvement. Here are a few suggestions:
> 
> * **Expanding the Summary:** The summary could be slightly more detailed, including specific references to the protocols and technologies mentioned in the abstract (SCTP, DTLS).
> * **Prioritizing Questions:** In the "Note to self" field, the model could prioritize the most critical questions for further investigation. This would help streamline the review process and ensure that the most pressing issues are addressed first.
> * **Cross-referencing:** As the model progresses through the document, it could benefit from cross-referencing information between different sections to identify inconsistencies or gaps in the proposal.
> 
> By incorporating these suggestions, the AI model could further refine its approach and become an even more valuable asset in the review of IETF Internet-Drafts.

### qwen-max-0428

> The model's approach to reviewing the IETF Internet-Draft appears well-structured and considerate of the guidelines set forth in the handbook. Here's a breakdown of its performance so far:
> 
> ### Positive Aspects:
> 1. **Adherence to Protocol**: The model correctly initiates the review process by requesting the first page with the command `$ page 1` and proceeds to follow the outlined steps, demonstrating an understanding of the terminal usage instructions.
> 2. **Comprehensive Summary**: The summary provided for page 1 succinctly captures the main points discussed, including the proposal's objective (removing SCTP checksum for efficiency), its application with DTLS, and the anticipation for further details.
> 3. **Thoughtful Note-Taking**: The "Note to self" field indicates proactive planning for future research, specifically mentioning the need to consult RFCs 7909 and 8422 to assess compatibility and security implications. This shows an intention to delve deeper into relevant standards and protocols, which is essential for a thorough review.
> 4. **Constructive Feedback**: The comment provided is constructive and directly related to the content of the abstract, indicating a focus on the document's substance rather than superficial elements. It appropriately requests more detailed explanations, which aligns with the review guidelines.
> 
> ### Areas for Potential Improvement or Consideration:
> - **Depth of Initial Comments**: While the comment is relevant, it could potentially benefit from including initial thoughts on the clarity and relevance of the problem statement or the potential impact of the proposal on existing systems, as these are also part of the reviewer's responsibilities.
> - **Future Context Awareness**: As the model progresses through the document, it might consider incorporating references to how subsequent sections relate to or build upon the information in previous pages. This would enhance the continuity and coherence of its feedback.
> 
> Overall, the model's first steps demonstrate a solid foundation in adhering to the review process and show promise in providing valuable insights once it has processed the entire document. Its systematic approach and planned investigation into related standards are commendable.
> 