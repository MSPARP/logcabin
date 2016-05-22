<%inherit file="/base.mako" />
<%block name="title">${request.context.name} - </%block>

<h1>${request.context.name}</h1>
<p id="author">by <a href="${request.route_path("users.profile", username=request.context.creator.username)}">${request.context.creator.username}</a></p>

<p id="summary">Summary: ${request.context.summary}</p>

<h2>Chapters</h2>
<ol>
  % for chapter in oldest_chapters:
  <li><a href="${request.route_path("logs.chapter", log_id=request.context.id, number=chapter.number)}">${chapter.name}</a></li>
  % endfor
</ol>
% if newest_chapters:
<% more_chapters = chapter_count - len(oldest_chapters) - len(newest_chapters) %>
<p>(<a href="${request.route_path("logs.chapters", log_id=request.context.id)}">${more_chapters} more chapter${"s" if more_chapters != 1 else ""}</a>)</p>
<ol start="${newest_chapters[0].number}">
  % for chapter in newest_chapters:
  <li><a href="${request.route_path("logs.chapter", log_id=request.context.id, number=chapter.number)}">${chapter.name}</a></li>
  % endfor
</ol>
% endif

