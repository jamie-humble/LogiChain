{/* <div class="row row-2 row--posts" style="margin-top: 50px;">
        <div class="col">
          <div class="card card--blog">
            <a href="https://www.webredone.com/blog/webredone-named-a-top-developer-in-serbia-by-clutch/" class="card__thumb" title="WebRedone Named a Top Developer in Serbia by Clutch">
              <div class="card__thumb__img" style="background-image: url('https://www.webredone.com/wp-content/uploads/2019/10/webredone-clutch-leader-hero-image.jpg')"></div>
            </a>
            <div class="card__content">
              <h3 class="card__title">
                <a href="https://www.webredone.com/blog/webredone-named-a-top-developer-in-serbia-by-clutch/" title="WebRedone Named a Top Developer in Serbia by Clutch">WebRedone Named a Top Developer in Serbia by Clutch</a>
              </h3>
              <p class="card__author card__posted"><span><span class="posted-on" rel="bookmark"><time class="entry-date published updated" datetime="Oct 31, 2019">Oct 31, 2019</time></span></span></p>
            </div>
          </div><!-- card -->
        </div><!-- col -->       
      </div>
    </div> */}

    // Data: link, title, image, date


var entry0 = {"link":"ProgressEntries/entry%230/ProgressPost.html","title":"Entry #0", "image":"Assets/fig1SC.PNG", "date":"Aug 7, 2021"};
var entry1 = {"link":"ProgressEntries/googledocs/googleDrive.html","title":"Google Drive", "image":"Assets/googleDriveBanner.png", "date":"Aug 13, 2021"};

var diction = [entry0,entry1];

const rows = document.getElementById("rows");

// main loop
diction.forEach(entry => {
  // creation
  const root = document.createElement("div");
  const card = document.createElement("div");
  const a0 = document.createElement("a");
  const img = document.createElement("div");
  const card_title = document.createElement("h3");
  const a1 = document.createElement("a");
  const card_author = document.createElement("p");
  const content = document.createElement("div");
  const bookmark = document.createElement("span");
  const time = document.createElement("time");

  root.className = "col";
    card.className = "card card--blog";
      a0.href = entry.link;
      a0.className = "card__thumb";
      a0.title = entry.title;
        img.className = "card__thumb__img";
        img.style = "background-image: url(" + entry.image + ")";
      content.className = "card__content";
        card_title.className = "card__title";
          a1.href = entry.link;
          a1.title = a1.innerHTML = entry.title;
        card_author.className = "card__author card__posted";
          bookmark.className = "posted-on bookmark";
            time.className = "entry-date published updated";
            time.dateTime = time.innerHTML = entry.date;

  // DOM distribution
  card_title.appendChild(a1);
  content.appendChild(card_title);
  bookmark.appendChild(time);
  card_author.appendChild(bookmark);
  content.appendChild(card_author);
  a0.appendChild(img);
  card.appendChild(a0);
  card.appendChild(content);
  root.appendChild(card);
  // final append
  rows.appendChild(root);

})