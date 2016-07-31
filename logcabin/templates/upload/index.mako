<%inherit file="/base.mako" />
<%block name="title">Upload or import - </%block>
<h1>Upload or import</h1>
<div id="content">
  % if cherubplay_chats:
  <section>
    <h2>Import from Cherubplay</h2>
    % for username, chats in cherubplay_chats.items():
    <h3>${username}</h3>
    <ul>
      % for chat in chats:
      <li><a href="${request.route_path("upload.cherubplay", username=username, url=chat["chat"]["url"])}">${chat["chat_user"]["title"] or chat["chat"]["url"]}</a></li>
      % endfor
    </ul>
    % endfor
  </section>
  % endif
  % if msparp_chats:
  <section>
    <h2>Import from MSPARP</h2>
    % for username, chats in msparp_chats.items():
    <h3>${username}</h3>
    <ul>
      % for chat in chats:
      <li><a href="${request.route_path("upload.msparp", username=username, url=chat["chat"]["url"])}">${chat["chat"]["title"]}</a></li>
      % endfor
    </ul>
    % endfor
  </section>
  % endif
</div>
