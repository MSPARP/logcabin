<%inherit file="/base.mako" />
<%block name="body_class">${"editable" if request.context.log.creator == request.user else ""}</%block>
<%block name="title">${request.context.log.name}, ${request.context.name} - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("logs.log", log_id=request.context.log.id)}">${request.context.log.name}</a></li>
    <li><a href="${request.route_path("logs.chapters", log_id=request.context.log.id)}">Chapters</a></li>
  </ul>
</nav>
<h1>${request.context.log.name}, ${request.context.name}</h1>
<article id="content" class="log_body">
  % if request.context.log.creator == request.user:
  <form action="${request.route_path("logs.chapter", log_id=request.context.log_id, number=request.context.number)}" method="post">
  % endif
    <header>
      <p>Summary: ${request.context.log.summary}</p>
    </header>
    <hr>
    % for message_revision in messages:
    <section id="message_${message_revision.message.id}">
      <div class="message_body">
        ${message_revision.html_text|n}
      </div>
      % if request.context.log.creator == request.user:
      <div class="controls">
        <a class="edit_link" href="${request.route_path("logs.chapter.message", log_id=request.context.log.id, number=request.context.number, message_id=message_revision.message.id)}">Edit</a>
        <label><input type="checkbox" name="delete_${message_revision.message.id}"> Delete</label>
      </div>
      % endif
    </section>
    % endfor
  % if request.context.log.creator == request.user:
  <button id="save_chapter" type="submit">Save</button>
  </form>
  % endif
</article>
