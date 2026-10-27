// Video in parts: plays part 1, loads the next part by itself, and keeps one speed for every part.
(function () {
  var box = document.querySelector(".player");
  if (!box) return;
  var video = box.querySelector("video");
  var source = video.querySelector("source");
  var buttons = Array.prototype.slice.call(box.querySelectorAll(".part"));
  var chips = Array.prototype.slice.call(box.querySelectorAll(".chip"));
  var KEY = "lab03-speed";
  var speed = 1;
  var current = 0;

  try {
    var saved = parseFloat(localStorage.getItem(KEY));
    if (chips.some(function (c) { return parseFloat(c.dataset.speed) === saved; })) speed = saved;
  } catch (e) { /* storage blocked: the page still works, the speed is just not remembered */ }

  function applySpeed() {
    video.defaultPlaybackRate = speed;  // a new src resets playbackRate to this
    video.playbackRate = speed;
    chips.forEach(function (c) { c.setAttribute("aria-pressed", parseFloat(c.dataset.speed) === speed ? "true" : "false"); });
  }

  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      speed = parseFloat(c.dataset.speed);
      try { localStorage.setItem(KEY, String(speed)); } catch (e) { /* see above */ }
      applySpeed();
    });
  });

  function captionsOn() {
    var shown = false, any = false;
    for (var i = 0; i < video.textTracks.length; i++) { any = true; if (video.textTracks[i].mode === "showing") shown = true; }
    return !any || shown;
  }

  function load(i, play) {
    var b = buttons[i];
    var on = captionsOn();
    current = i;
    Array.prototype.slice.call(video.querySelectorAll("track")).forEach(function (t) { t.remove(); });
    source.setAttribute("src", b.dataset.src);
    var track = document.createElement("track");
    track.kind = "subtitles";
    track.srclang = box.dataset.lang;
    track.label = box.dataset.subsLabel;
    track.src = b.dataset.vtt;
    video.appendChild(track);
    track.track.mode = on ? "showing" : "disabled";
    video.poster = b.dataset.poster;
    video.load();
    applySpeed();
    buttons.forEach(function (x, k) { if (k === i) x.setAttribute("aria-current", "true"); else x.removeAttribute("aria-current"); });
    if (play) { var p = video.play(); if (p && p.catch) p.catch(function () { /* the browser wants a click first */ }); }
  }

  buttons.forEach(function (b, i) { b.addEventListener("click", function () { load(i, true); }); });
  video.addEventListener("ended", function () { if (current < buttons.length - 1) load(current + 1, true); });
  video.addEventListener("loadedmetadata", applySpeed);
  applySpeed();
})();
