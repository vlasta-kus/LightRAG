from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

#"product (anything produced/sold, e.g. machines, tools, components, substances etc.)"
PROMPTS["DEFAULT_ENTITY_TYPES"] = [
    "organization", "person_or_title (specific business title/role or person name)", "document (id or title of any concrete complete physical or electronic document, not just its fragment)", 
    "process (a high-level process, procedure, plan, or any set of steps/tasks/activities; e.g. change management process, Corrective Procedure etc.)", 
    "activity (any task, activity or event; e.g. Quality Validation, QA Inspection, machine downtime, etc.)", 
    "device (any kind of machine, device, tool, device component ...)", 
    "object (any kind of physical object not used to do work)", 
    "material_or_substance", 
    "other (any other relevant specific manufacturing-related entity)"
]

PROMPTS["DEFAULT_USER_PROMPT"] = "n/a"

PROMPTS["entity_extraction"] = """---Goal---
Given a text document that is potentially relevant to building a Knowledge Graph in manufacturing domain and a list of entity types, identify all relevant entities and relationships among the entities. 
The KG will be built from data from different manufacturing projects with sometimes overlapping concepts (entities).
Use {language} as output language.

---Steps---
1. Read the input text and the provided list of entity types. Consider carefully which concepts and information to model as KG entities and which as relationships, and which detailed information to consider an attribute of an entity vs an attribute of a relationship.
- entities should have specific names - avoid creation of super nodes like "machine" or "responsible"
- entity attributes / descriptions should be usable and useful across documents from different (but often partly related) manufacturing projects; for example, multiple projects will likely have Predictive Maintenance process node, but different project-specific details - put those details to relationships
- edges represent specific details of a relation between two entities based on the current input text / project
The goal is to build a multi-project KG that captures the essential higher-level manufacturing & engineering knowledge. Avoid information duplicates in node vs edge descriptions.

2. Identify all entities according to the list of entity types and extract the following information:
- entity_name: Name of the entity, use same language as input text. Avoid too generic entity names: always attempt to identify concrete full entity name based on the whole context!
- entity_type: One of the following types (here stated optionally with descriptions or examples in the round brackets): [{entity_types}]
- entity_description: Straightforward brief description of the entity and its key general attributes that are relevant across different data sources. More specific details (such as (sub)project specific) belong to the descriptions of relationships from the following step. The entity description must always be grounded in the text, don't make it up! If no such description can be generated, output an empty string.
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

3. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation how the source and target entities are related (specific details; example: a date of commencing work on a new device); must always be grounded in the text, don't make it up!
- relationship_strength: a numeric score (1 to 10) indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

4. Identify high-level keywords that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level keywords as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

5. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

6. When finished, output {completion_delimiter}

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Entity_types: [{entity_types}]
Text:
{input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [document (id or title of any concrete physical or electronic document), person_or_title, process (a process, procedure, plan, or any set of steps/tasks; e.g. change management process, Corrective Procedure etc.), activity (any task, activity or event; e.g. Quality Validation, QA Inspection, machine downtime, etc.), other]
Text:
```
Emphasis shall be put on preventive maintenance, to ensure equipment operates without unexpected down time or error. Correcting a fault in a machine after it breaks is considered repair, and not maintenance. The purpose of a robust preventive maintenance program is to eliminate 
the need for unscheduled repairs and down time.

1.3.1. General
Preventive maintenance records must be kept for each unique piece of key process equipment. This record will contain, at a minimum:
- Type of device
- Manufacturer
- Model number
- Serial number
Manufacturers often issue guidelines. Preventive Maintenance tasks shall be based on these guidelines, but may be overridden or altered to suit the company’s specific needs, based on equipment usage, criticality to quality, etc.
Those that are done daily, hourly, “before use” or at a more frequent basis, the need for a record is not required. Records must be maintained for any task performed at a frequency of weekly or greater (use Machine Maintenance section of the Preventive Maintenance Log).

1.3.2. Quality Objectives
The Quality Objectives are designed to provide a meaningful measure of the company to agreed targets set by the management team. Targets are based on significant risks, reviewed periodically and changed to reflect the company’s commitment to continual improvement.
The company is dedicated to continual improvement and quality maintenance.
Human resources to deliver the maintenance are provided by the responsible manager (“Who by” section).
```

Output:
("entity"{tuple_delimiter}"Preventive Maintenance"{tuple_delimiter}"process"{tuple_delimiter}"Aims to eliminate unscheduled machine repairs and downtime through proactive measures to address issues before failure occurs."){record_delimiter}
("entity"{tuple_delimiter}"Preventive Maintenance Log"{tuple_delimiter}"document"{tuple_delimiter}"Records of Preventive Maintenance tasks performed on weekly or greater basis."){record_delimiter}
("entity"{tuple_delimiter}"manufacturer's guidelines"{tuple_delimiter}"process"{tuple_delimiter}"Recommended processes issued by manufacturers that serve as the basis for machine and equipment maintenance."){record_delimiter}
("entity"{tuple_delimiter}"Quality Objectives"{tuple_delimiter}"process"{tuple_delimiter}"They provide a measure of company targets, based on periodically reviewed significant risks, set by the management team."){record_delimiter}
("relationship"{tuple_delimiter}"Preventive Maintenance"{tuple_delimiter}"Preventive Maintenance Log"{tuple_delimiter}"Records of Preventive Maintenance tasks must be kept in Preventive Maintenance Log's Machine Maintenance section, containing at a minimum Type of device, Manufacturer, Model number, Serial number."{tuple_delimiter}"documentation requirements, compliance tracking"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Preventive Maintenance"{tuple_delimiter}"manufacturer's guidelines"{tuple_delimiter}"Preventive Maintenance activities are based on manufacturer’s guidelines and internal company needs. They ensure equipment reliability, production quality, etc."{tuple_delimiter}"maintenance guidelines, customization"{tuple_delimiter}10){record_delimiter}
("content_keywords"{tuple_delimiter}"preventive maintenance, equipment reliability, operational strategy, documentation"){completion_delimiter}
#############################""",
    """Example 2:

Entity_types: [document (id or title of any concrete physical or electronic document), organization, process (a process, procedure, plan, or any set of steps/tasks), activity (any task, activity or event; e.g. Quality Validation, QA Inspection, machine downtime, etc.), device (any kind of machine, device, tool, component ...), object (any kind of physical object that is not a product), material_or_substance, other]
Text:
```
CERN, the European Organization for Nuclear Research, has a seat is in Geneva but its premises are located on both sides of the French-Swiss border. CERN’s mission is to enable international collaboration in the field of high-energy particle physics research.
The Compact Muon Solenoid (CMS, https://home.cern/science/experiments/cms) experiment, located in CERN’s LHC accelerator, will undergo a major modification, the CMS Phase 2 Upgrade.
A new tracking detector system shall be constructed, with one of the sub-detectors being TBPS, whose design is the subject of this document. The TBPS will contain 12 laminated Interconnection Rings that join the three concentric layers of the TBPS. For physics measurement reasons the TBPS structures shall be light,
stiff and dimensionally stable, leading the material choice to cutting edge composites, such as carbon-fibre/foam structures.
...

## 2.3 Inspection Tools
Redwire will utilise various inspection tools in the validation of the TBPS rings:
* Trimos high accuracy digital height gauge
* Nikon 3D precision laser scanner
...

## 3. Final Sign Off
Name: John Snow
Job Title: Project Manager
Date (expected): 19/10/1918
Activities: see "Responsibilities" column
```

Output:
("entity"{tuple_delimiter}"CERN"{tuple_delimiter}"organization"{tuple_delimiter}"CERN, the European Organization for Nuclear Research, headquartered in Geneva, enables high-energy particle physics research."){record_delimiter}
("entity"{tuple_delimiter}"Compact Muon Solenoid (CMS)"{tuple_delimiter}"device"{tuple_delimiter}"A particle physics experiment at CERN's LHC accelerator."){record_delimiter}
("entity"{tuple_delimiter}"CMS Phase 2 Upgrade"{tuple_delimiter}"activity"{tuple_delimiter}"A major modification of the CMS experiment."){record_delimiter}
("entity"{tuple_delimiter}"LHC"{tuple_delimiter}"device"{tuple_delimiter}"A particle accelerator at CERN."){record_delimiter}
("entity"{tuple_delimiter}"TBPS"{tuple_delimiter}"device"{tuple_delimiter}"A sub-detector within the tracking detector system at the CMS experiment at CERN."){record_delimiter}
("entity"{tuple_delimiter}"Interconnection Ring"{tuple_delimiter}"device"{tuple_delimiter}"A laminated component that joins the three concentric layers of the TBPS sub-detector."){record_delimiter}
("entity"{tuple_delimiter}"carbon-fibre/foam composites"{tuple_delimiter}"material_or_substance"{tuple_delimiter}"Light, stiff and dimensionally stable construction material."){record_delimiter}
("entity"{tuple_delimiter}"Redwire"{tuple_delimiter}"organization"{tuple_delimiter}""){record_delimiter}
("entity"{tuple_delimiter}"Trimos height gauge"{tuple_delimiter}"device"{tuple_delimiter}"High accuracy digital height gauge."){record_delimiter}
("entity"{tuple_delimiter}"Nikon 3D laser scanner"{tuple_delimiter}"device"{tuple_delimiter}"Precision laser scanner."){record_delimiter}
("entity"{tuple_delimiter}"In-Process Inspection"{tuple_delimiter}"process"{tuple_delimiter}""){record_delimiter}
("entity"{tuple_delimiter}"John Snow"{tuple_delimiter}"person_or_title"{tuple_delimiter}"John Snow is a Project Manager."){record_delimiter}
("relationship"{tuple_delimiter}"LHC"{tuple_delimiter}"CERN"{tuple_delimiter}"LHC accelerator is a particle accelerator at CERN."{tuple_delimiter}"scientific research, accelerator, particle physics"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Compact Muon Solenoid (CMS)"{tuple_delimiter}"LHC"{tuple_delimiter}"The CMS particle physics research experiment at the LHC accelerator."{tuple_delimiter}"scientific research, particle physics"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"CMS Phase 2 Upgrade"{tuple_delimiter}"Compact Muon Solenoid (CMS)"{tuple_delimiter}"CMS Phase 2 Upgrade is a major planned modification of the CMS experiment."{tuple_delimiter}"device upgrade, particle detector"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"TBPS"{tuple_delimiter}"CMS Phase 2 Upgrade"{tuple_delimiter}"TBPS is part of the CMS Phase 2 Upgrade."{tuple_delimiter}"system upgrade, particle detector"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"TBPS"{tuple_delimiter}"CMS"{tuple_delimiter}"TBPS will be a sub-detector of the particle tracking detector system at the CMS experiment."{tuple_delimiter}"particle detector, device subsystem"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"TBPS"{tuple_delimiter}"Interconnection Ring"{tuple_delimiter}"TBPS includes 12 Interconnection Rings that connect its three concentric layers."{tuple_delimiter}"structural component, subsystem integration"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"TBPS"{tuple_delimiter}"carbon-fibre/foam composites"{tuple_delimiter}"TBPS will be constructed using carbon-fibre/foam composites."{tuple_delimiter}"material selection, performance optimization"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Redwire"{tuple_delimiter}"Interconnection Ring"{tuple_delimiter}"Redwire will inspect the rings."{tuple_delimiter}"inspection, validation"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Interconnection Ring"{tuple_delimiter}"Trimos height gauge"{tuple_delimiter}"The rings will be inspected by a Trimos height gauge."{tuple_delimiter}"inspection, validation"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Interconnection Ring"{tuple_delimiter}"Nikon 3D laser scanner"{tuple_delimiter}"The rings will be inspected by a Nikon 3D laser scanner."{tuple_delimiter}"inspection, validation"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"John Snow"{tuple_delimiter}"TBPS"{tuple_delimiter}"The Project Manager John Snow is expected to sign off the TBPS project on 19/10/1918."{tuple_delimiter}"project management"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"particle physics, detector upgrade, subsystem design, composite materials"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: [economic_policy, athlete, event, location, record, organization, equipment]
Text:
```
At the World Athletics Championship in Tokyo, Noah Carter broke the 100m sprint record using cutting-edge carbon-fiber spikes.
```

Output:
("entity"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"event"{tuple_delimiter}"The World Athletics Championship is a global sports competition featuring top athletes in track and field."){record_delimiter}
("entity"{tuple_delimiter}"Tokyo"{tuple_delimiter}"location"{tuple_delimiter}"Tokyo is the host city of the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"athlete"{tuple_delimiter}"Noah Carter is a sprinter who set a new record in the 100m sprint at the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"record"{tuple_delimiter}"The 100m sprint record is a benchmark in athletics, recently broken by Noah Carter."){record_delimiter}
("entity"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"equipment"{tuple_delimiter}"Carbon-fiber spikes are advanced sprinting shoes that provide enhanced speed and traction."){record_delimiter}
("entity"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"organization"{tuple_delimiter}"The World Athletics Federation is the governing body overseeing the World Athletics Championship and record validations."){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"Tokyo"{tuple_delimiter}"The World Athletics Championship is being hosted in Tokyo."{tuple_delimiter}"event location, international competition"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"Noah Carter set a new 100m sprint record at the championship."{tuple_delimiter}"athlete achievement, record-breaking"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"Noah Carter used carbon-fiber spikes to enhance performance during the race."{tuple_delimiter}"athletic equipment, performance boost"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"The World Athletics Federation is responsible for validating and recognizing new sprint records."{tuple_delimiter}"sports regulation, record certification"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"athletics, sprinting, record-breaking, sports technology, competition"){completion_delimiter}
#############################""",
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities,
concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language. Output directly the summary right away, without any other explanatory text.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS["entity_continue_extraction"] = """
MANY entities and relationships were missed in the last extraction.

---Remember Steps---

1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

---Output---

Add them below using the same format:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---'

It appears some entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["fail_response"] = (
    "Sorry, I'm not able to provide an answer to that question.[no-context]"
)

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to user query about Knowledge Graph and Document Chunks provided in JSON format below.


---Goal---

Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. Do not include information not provided by Knowledge Base.

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Graph and Document Chunks---
{context_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Document (DOC), and include the file path if available, in the following format: [KG/DOC] file_path
- If you don't know the answer based on the provided context, just say so.
- Do not make anything up - always ground the answer in the provided context. Do not include information not provided by the Knowledge Base.
- Addtional user prompt: {user_prompt}

Response:"""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query and conversation history.

---Goal---

Given the query and conversation history, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes or actions (relationships in a Knowledge Graph), while low-level keywords focus on specific entities, details, or concrete terms (entities in a Knowledge Graph).

---Instructions---

- Consider both the current query and relevant conversation history when extracting keywords
- Output the keywords in JSON format, it will be parsed by a JSON parser, do not add any extra content in output
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes or actions
  - "low_level_keywords" for specific entities or details

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Conversation History:
{history}

Current Query: {query}
######################
The `Output` should be human text, not unicode characters. Keep the same language as `Query`.
Output:

"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How can I minimize the impact of machine downtime on production?"
################
Output:
{
  "high_level_keywords": ["machine downtime", "production optimization", "operational continuity", "downtime mitigation"],
  "low_level_keywords": ["machine failure", "root cause analysis", "preventive maintenance", "real-time monitoring", "automation"]
}
#############################""",
    """Example 2:

Query: "I just found some foreign object debris (FODs) in my product, how do I prevent this from happening?"
################
Output:
{
  "high_level_keywords": ["foreign object debris (FODs) prevention", "product quality control", "manufacturing contamination"],
  "low_level_keywords": ["foreign object debris (FODs)", "inspection procedures", "quality ensurance process", "debris containment"]
}
#############################""",
    """Example 3:

Query: "Give me a summary of the issues on the Volkswagen Aerocovers."
################
Output:
{
  "high_level_keywords": ["product issues", "manufacturing quality", "customer complaints"],
  "low_level_keywords": ["Volkswagen", "aerocovers", "wheel accessory"]
}
#############################""",
]

PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Document Chunks provided provided in JSON format below.

---Goal---

Generate a concise response based on Document Chunks and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Document Chunks, and incorporating general knowledge relevant to the Document Chunks. Do not include information not provided by Document Chunks.

When handling content with timestamps:
1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content and the timestamp
3. Don't automatically prefer the most recent content - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Document Chunks(DC)---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating each source from Document Chunks(DC), and include the file path if available, in the following format: [DC] file_path
- If you don't know the answer, just say so.
- Do not include information not provided by the Document Chunks.
- Addtional user prompt: {user_prompt}

Response:"""

# TODO: deprecated
PROMPTS[
    "similarity_check"
] = """Please analyze the similarity between these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate whether these two questions are semantically similar, and whether the answer to Question 2 can be used to answer Question 1, provide a similarity score between 0 and 1 directly.

Similarity score criteria:
0: Completely unrelated or answer cannot be reused, including but not limited to:
   - The questions have different topics
   - The locations mentioned in the questions are different
   - The times mentioned in the questions are different
   - The specific individuals mentioned in the questions are different
   - The specific events mentioned in the questions are different
   - The background information in the questions is different
   - The key conditions in the questions are different
1: Identical and answer can be directly reused
0.5: Partially related and answer needs modification to be used
Return only a number between 0-1, without any additional content.
"""
