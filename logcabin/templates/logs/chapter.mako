<%inherit file="/base.mako" />
<%block name="title">${request.context.log.name}, ${request.context.name} - </%block>
  <nav id="breadcrumb">
    <ul>
      <li><a href="${request.route_path("logs.log", log_id=request.context.log.id)}">${request.context.log.name}</a></li>
      <li><a href="${request.route_path("logs.chapters", log_id=request.context.log.id)}">Chapters</a></li>
    </ul>
  </nav>
  <article id="log_body">
    <header>
      <h1>${request.context.log.name}, ${request.context.name}</h1>
      <p>log info description tags etc</p>
    </header>
    % for message_revision, message in messages:
    <section id="message${message.id}">
      ${message_revision.text}
    </section>
    % endfor
  </article>

