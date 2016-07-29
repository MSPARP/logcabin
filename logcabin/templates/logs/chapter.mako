<%inherit file="/base.mako" />
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
      <p>log info description tags etc</p>
    </header>
    % for message_revision in messages:
    <section id="message${message_revision.message.id}">
      ${message_revision.html_text|n}
      % if request.context.log.creator == request.user:
      <a href="${request.route_path("logs.chapter.message", log_id=request.context.log.id, number=request.context.number, message_id=message_revision.message.id)}">Edit</a>
      <label><input type="checkbox" name="delete_${message_revision.message.id}"> Delete</label>
      % endif
    </section>
    % endfor
  % if request.context.log.creator == request.user:
  <button id="save_chapter" type="submit">Save</button>
  </form>
  % endif
</article>
