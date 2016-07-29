<%inherit file="/base.mako" />
<%block name="title">Chapters in ${request.context.name} - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("logs.log", log_id=request.context.id)}">${request.context.name}</a></li>
  </ul>
</nav>
<h1>Chapters in ${request.context.name}</h1>
<div id="content">
  <ol>
    % for chapter in chapters:
    <li><a href="${request.route_path("logs.chapter", log_id=request.context.id, number=chapter.number)}">${chapter.name}</a></li>
    % endfor
  </ol>
</div>
