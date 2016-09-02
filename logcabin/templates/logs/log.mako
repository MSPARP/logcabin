<%inherit file="/base.mako" />
<%block name="title">${request.context.name} - </%block>
<h1>${request.context.name}</h1>
% if not request.context.posted_anonymously:
<p id="author">by <a href="${request.route_path("users.profile", username=request.context.creator.username)}">${request.context.creator.username}</a></p>
% endif
<div id="content">
  <p>Rating: ${request.context.rating_name}</p>
  <p id="summary">Summary: ${request.context.summary}</p>
  % if own_favorite:
  <form action="${request.route_path("logs.unfavorite", log_id=request.context.id)}" method="post">
    <button type="submit">Unfavorite</button>
  </form>
  % elif request.user:
  <form action="${request.route_path("logs.favorite", log_id=request.context.id)}" method="post">
    <button type="submit">Favorite</button>
  </form>
  % endif
  % if favorites:
  <h2>Favorited by</h2>
  <ul>
    % for favorite in favorites:
    % if favorite.user == request.user:
    <li>You</li>
    % else:
    <li><a href="${request.route_path("users.profile", username=favorite.user.username)}">${favorite.user.username}</a></li>
    % endif
    % endfor
  </ul>
  % endif
  <h2>Fandoms</h2>
  <ul>
    % for fandom in log.fandoms:
    <li><a href="${request.route_path("fandoms.fandom", category_url_name=fandom.category.url_name, fandom_url_name=fandom.url_name)}">${fandom.name}</a></li>
    % endfor
  </ul>
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
  % if sources:
  <h2>Source${"s" if len(sources) > 1 else ""}</h2>
  <ul>
    % for source, chat_log, user_account in sources:
    <li>
      % if source.type == "cherubplay":
      <p><a href="${request.registry.settings["urls.cherubplay"]}/chats/${source.url}/" target="_blank">${chat_log["chat_user"]["title"] if chat_log and chat_log["chat_user"] and chat_log["chat_user"]["title"] else source.url}</a></p>
      <p>
        From Cherubplay,
        % if user_account:
        via ${user_account["username"]}.
        % else:
        anonymously.
        % endif
      </p>
      <p>Auto-import ${"enabled" if source.auto_import else "disabled"}, last import ${source.last_import}.</p>
      % endif
    </li>
    % endfor
  </ul>
  % endif
</div>
