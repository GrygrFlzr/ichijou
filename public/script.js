(() => {
  // do stuff
  const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  Array.from(document.querySelectorAll("time[datetime]")).forEach((el) => {
    const ms_diff = Date.parse(el.dateTime) - Date.now();
    const seconds_diff = ms_diff / 1000;
    const minutes_diff = seconds_diff / 60;
    const hours_diff = minutes_diff / 60;
    const days_diff = hours_diff / 24;
    const weeks_diff = days_diff / 7;
    if (weeks_diff >= 1) {
      el.innerText = rtf.format(Math.floor(weeks_diff), "week");
    } else if (weeks_diff <= -1) {
      el.innerText = rtf.format(Math.ceil(weeks_diff), "week");
    } else if (days_diff > 0) {
      el.innerText = rtf.format(Math.floor(weeks_diff), "day");
    } else {
      el.innerText = rtf.format(Math.ceil(weeks_diff), "day");
    }
  });
})();
