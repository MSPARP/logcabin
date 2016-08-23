<%inherit file="/base.mako" />
<%block name="title">Fandoms - </%block>
<h1>Fandoms</h1>
<div id="content">
  <ul>
    % for category in categories:
    <li><a href="${request.route_path("fandoms.category", category_url_name=category.url_name)}">${category.name}</a></li>
    % endfor
  </ul>
</div>
