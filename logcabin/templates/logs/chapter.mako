<%inherit file="/base.mako" />
<%block name="title">${request.context.log.name}, ${request.context.name} - </%block>
  <article id="log_body">
    <header>
      <h1>${request.context.log.name}, ${request.context.name}</h1>
      <p>log info description tags etc</p>
    </header>
    % for message in messages:
    <section id="message${message.id}">
      ${message.html}
    </section>
    % endfor
  </article>

