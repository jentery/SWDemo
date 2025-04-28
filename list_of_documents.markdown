---
layout: page
title: Index of Files
permalink: /mdfiles/
---

Below is a list of all the files hosted on this demo page ordered alphabetically:

<ul>
  {% assign documents = site.pages | where_exp: "page", "page.permalink contains '/output_documents/'" | sort: "title_of_doc" %}
  {% for page in documents %}
    <li>
      <a href="{{ page.permalink }}">{{ page.title_of_doc }}</a>
      <br><small>By {{ page.first_name }} {{ page.last_name }} — {{ page.institution }}</small>
    </li>
  {% endfor %}
</ul>