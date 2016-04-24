<%inherit file="/base.mako" />
<%block name="title">Chapters in ${request.context.name} - </%block>

<h1>Chapters in ${request.context.name}</h1>

<ol>
  % for chapter in chapters:
  <li><a href="${request.route_path("logs.chapter", log_id=request.context.id, number=chapter.number)}">${chapter.name}</a></li>
  % endfor
</ol>
