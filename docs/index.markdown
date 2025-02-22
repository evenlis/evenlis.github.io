---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
title: Fon barnehage
---

# Oversikt
<style type="text/css">
    body {
        width: 70%;
    }
    div.home {
        width: 100%;
    }
    div.wrapper {
        width: 100%;

    }
    .page-content {
        width: 170%;
    }
    .barnehagetabell {
        table-layout: fixed;
        width: 100%;
    }
</style>

<table class="barnehagetabell">
  {% for row in site.data.barnehager_sammenligning %}
    {% if forloop.first %}
    <tr>
      {% for pair in row %}
        <th>{{ pair[0] }}</th>
      {% endfor %}
    </tr>
    {% endif %}
    {% tablerow pair in row %}
      {{ pair[1] }}
    {% endtablerow %}
  {% endfor %}
</table>


