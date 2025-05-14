---
layout: page
title: The Collection
permalink: /mdfiles/
---

The following materials include course outlines, assignments, prompts, and workshop instructions for literary sound studies. They are ordered alphabetically according to title. 

Note that these materials appear as they were originally written for teaching and learning. We did not edit them. We only formatted them for the purposes of collection. 

<ul>
  {% assign documents = site.output_documents | where_exp: "page", "page.permalink contains '/output_documents/'" | sort: "title" %}
  {% for page in documents %}
    <li>
      <a href="{{ site.baseurl }}{{ page.permalink }}">{{ page.title_of_doc }}</a>
      <br><small>By {{ page.first_name }} {{ page.last_name }} — {{ page.institution }}</small>
    </li>
  {% endfor %}
</ul>
