(function($) {
  "use strict";

  // Imports
  const utils = window.app.utils;
  const ApiClient = window.app.ApiClient;
  const FrequencyGauge = window.app.FrequencyGauge;

  /**
   * Parse Service
   * 
   * Responsible for submitting parse requests to the backend, storing data,
   * and querying the returned data.
   */
  var parseService = {
    url: "/api/parsetext?html=y",
    data: null,
    error: false,
    parse: function(text) {
      var jqXhr = $.ajax ({
        type: "POST",
        url: this.url,
        dataType: "json",
        contentType: "application/json",
        data: JSON.stringify({text: text})
      });

      var handleSuccess = function(data, textStatus) {
        console.log("parse successful: ", textStatus);
        this.data = data;
        this.error = false;
      }.bind(this);

      var handleError = function(jqXhr, textStatus, errorThrown) {
        var error, res, reason, traceback;
        console.log("parse error: ", textStatus, errorThrown);
        try {
          res = JSON.parse(jqXhr.responseText);
          reason = (res.error && res.error.reason) || "Unknown error [1] - response did not provide error details";
          traceback = (res.error && res.error.traceback) || "";
          error = {"reason": reason, "traceback": traceback};
        } catch(caughtError) {
          console.log(caughtError);
          error = {"reason": "Unknown error [2] - failed to parse error response"};
        }
        this.data = null;
        this.error = error;
        console.log(error);
      }.bind(this);

      jqXhr.then(handleSuccess, handleError);

      return jqXhr;
    },
    getWordInfo: function(form_ids) {
      var data = this.data;
      if(!data || !form_ids || form_ids.length == 0) {
        return null;
      }
      var distinct_lemmas = {};
      var word_info = {forms: [], lemmas: []};
      var form_id, form, lemma;
      for(var i = 0; i < form_ids.length; i++) {
        form_id = form_ids[i];
        form = data.forms[form_id];
        lemma = data.lemmas[form.lemma_id];
        word_info.forms.push(form);
        distinct_lemmas[lemma.id] = lemma;
      }
      for(var lemma_id in distinct_lemmas) {
        if(distinct_lemmas.hasOwnProperty(lemma_id)) {
          word_info.lemmas.push(distinct_lemmas[lemma_id]);
        }
      }
      return word_info;
    }
  };

  /**
   * Parsed Text Controller
   * 
   * Responsible for rendering and manipulating the parsed text.
   */
  var parsedTextCtrl = {
    render: function(data) {
      $("#analysis").removeClass("d-none");
      $("#parsed").html(data.html);
      this.updateWordsWithMultiple();
    },
    reset: function() {
      $('#parsed').html('');
    },
    getElementDataFormIds: function(el) {
      var form_ids = $(el).data("form-ids") || "";
      return String(form_ids).split(",");
    },
    toggleMultiple: function() {
      $('.multiple').toggleClass('underline');
    },
    toggleLemmas: function() {
      var self = this;
      if(!self.hasOwnProperty("showLemmas")) {
        self.showLemmas = false;
      }
      self.showLemmas = !self.showLemmas;
  
      $(".word.parsed").each(function(idx, el) {
        var form_ids = self.getElementDataFormIds(el);
        var word_info = parseService.getWordInfo(form_ids);
        var form, lemma, is_capitalized;
        if(word_info) {
          if(self.showLemmas) {
            form = $(el).html();
            is_capitalized = (form.charAt(0) == form.charAt(0).toUpperCase());
            lemma = word_info.lemmas[0].label;
            lemma = (is_capitalized ? lemma.charAt(0).toUpperCase() + lemma.substr(1) : lemma);
            $(el).data("form", form);
            $(el).html(lemma);
          } else {
            $(el).html($(el).data("form"));
          }
        }
      });
    },
    updateWordsWithMultiple: function() {
      var self = this;
      $(".word.parsed").each(function(idx, el) {
        var form_ids = self.getElementDataFormIds(el);
        if(form_ids.length > 1) {
          $(el).addClass("multiple");
        }
      });
    }
  };

  /**
   * Word Info Controller
   * 
   * Responsible for rendering word information alongside the parsed text.
   */
  var wordInfoCtrl = {
    render: function(word_info) {
      if(word_info) {
        $("#worddetails").html(this.template(word_info));
        $("#wordvis").html("");
        this.updateVis(word_info);
      } else {
        $("#worddetails").html("");
        $("#wordvis").html("");
      }
      
    },
    setPosition: function(position) {
      var top = parseInt(position.top, 10);
      if(top) {
        $("#wordinfo").css({"top": top+"px"});
      } else {
        $("#wordinfo").css({"top": ""});
      }
    },
    reset: function() {
      $("#worddetails").html("Click on a word.");
      $("#wordvis").html("");
    },
    template: function(word_info) {
      var form = word_info.forms[0].label;
      var fields = ['label', 'pos', 'aspect', 'level', 'translation'];
      var data = {};
      word_info.lemmas.forEach(function(lemma) {
        fields.forEach(function(key) {
          if(!(key in data)) {
            data[key] = [];
          }
          if(lemma[key] && data[key].indexOf(lemma[key]) == -1) {
            data[key].push(lemma[key]);
          }
        });
      });
      word_info.forms.forEach(function(form) {
        if(!("type" in data)) {
          data.type = [];
        }
        if(form.type && data.type.indexOf(form.type) == -1) {
          data.type.push(form.type);
        }
      });

      var html = '<h3 class="wordtitle inline d-block">'+form+'</h3>';
      if(data.label.length > 0) {
        html += '<span>Lemma:</span> <span class="textinfoval">' + data.label.join(", ") + "</span><br>";
      }
      html += '<span>Parts of Speech:</span> <span class="textinfoval">' + data.pos.join(", ") + "</span><br>";
      if(data.aspect.length > 0) {
        html += '<span>Aspect:</span> <span class="textinfoval">' + data.aspect.join(", ") + "</span><br>";
      }
      html += '<span>Levels:</span> <span class="textinfoval">' + data.level.join(", ") + "</span><br>";
      html += '<span>Inflections:</span> <span class="textinfoval">' + data.type.join(", ") + "</span><br>";
      html += '<span>Translation:</span> <span class="textinfoval">' + (data.translation.join(", ") || "n/a") + "</span><br>";
      return html;
    },
    updateVis: function(word_info) {
      if(word_info.lemmas.length != 1) {
        return;
      }
      var lemma = word_info.lemmas[0];
      this._updateVerbFrequencyGauge(lemma);
    },
    _updateVerbFrequencyGauge: function(lemma) {
      var vis_data = [];
      if(lemma.pos == "verb") {
        var aspect_pair = (lemma.aspect_pair && lemma.aspect_pair.length == 2) ? lemma.aspect_pair : [];
        vis_data = aspect_pair.map((v) => { 
          return {"label": v.lemma_label, "value": v.lemma_count, "description": v.aspect}
        });
        $("#wordvis").append("<span>Frequency:</span>");
        var gauge = new FrequencyGauge({ 
          parentElement: "#wordvis",
          config: { colors: ['#b74c4c', '	#999']} 
        });
        gauge.data(vis_data).draw();
      } 
    }
  };

  /**
   * Text Info Controller
   * 
   * Responsible for displaying and manipulating statistics about the parsed text.
   */
  var textInfoCtrl = {
    render: function(data) {
      this.counts = this.getCounts();
      this.generateChart();
      this.showTextInfo();
    },
    reset: function() {
      this.counts = null;
      $("#levels").html('');
      $("#textinfo").html('');
    },
    getCounts: function() {
      var counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0};
      $('.word[data-level]').each(function(index, el) {
          counts[parseInt($(el).attr("data-level")[0])] += 1;
      });
      counts[0] = $('.word').length - $('.word[data-level]').length;
      counts.total = counts[0] + counts[1] + counts[2] + counts[3] + counts[4];
      return counts;
    },
    generateChart: function() {
      var counts = this.counts;
      var colors = {L_: '#333333', L1: 'green', 'L1-2': 'green', L2: 'blue', L3: '#8000ff', L4: 'orange', L5: 'orange' };
      var maskCls = {L_: "level0", L1: "level1", 'L1-2': 'level1-2', L2: 'level2', L3: 'level3', L4: 'level4', L5: 'level5'};
      
      var onclick = function (d, i) { 
        console.log("onclick", d, i); 
        var cls = maskCls[d.id]
        var el = document.querySelector(".words");
        if(el.classList.contains(cls)) {
          el.className = "words";
        } else {
          el.className = "words mask " + cls;
        }
      };

      var order = function(a, b) {
        var a_level = a.id.charAt(1);
        var b_level = b.id.charAt(1);
        if(a_level == "_") {
          return 1;
        } else if(b_level == "_") {
          return -1;
        }
        return parseInt(a_level, 10) - parseInt(b_level, 10);
      };

      var char1 = c3.generate({
        bindto: '#chart-bar',
        data: {
            type: 'bar',
            columns: [
                ['L1', counts[1]],
                ['L2', counts[2]],
                ['L3', counts[3]],
                ['L4', counts[4]],
                ['L_', counts[0]],
            ],
            groups: [
              ['L1'],
              ['L2'],
              ['L3'],
              ['L4'],
              ['L_']
            ],
            labels: {
              format: function(v, id, i, j) { return d3.format('.1%')(v / counts.total) }
            },
            order: order,
            colors: colors,
            onclick: onclick,
        },
        tooltip: {
          show: false
        }
      });

      var char2 = c3.generate({
        bindto: '#chart-pie',
        data: {
            type: 'pie',
            columns: [
                ['L1-2', counts[1]+counts[2]],
                ['L3', counts[3]],
                ['L4', counts[4]],
                ['L_', counts[0]],
            ],
            colors: colors,
            onclick: onclick,
            order: order
        }
      }); 
    },
    showTextInfo: function() {
      var counts = this.counts;
      var wl = $('.word').length;
      var html = '';
      html += '<div>Word Count: <span class="numbers mr-4"> ' + wl + '</span></div>';
      html += '<div>Unparsed Count: <span class="numbers mr-4"> ' + counts[0] + '</span></div>';
      html += '<div>L1 Count: <span class="numbers mr-4"> ' + counts[1] + '</span></div>';
      html += '<div>L2 Count: <span class="numbers mr-4"> ' + counts[2] + '</span></div>';
      html += '<div>L3 Count: <span class="numbers mr-4"> ' + counts[3] + '</span></div>';
      html += '<div>L4 Count: <span class="numbers mr-4"> ' + counts[4] + '</span></div>';
      html += '<button type="button" id="textinfocopy" class="btn btn-secondary btn-sm">Copy to clipboard</button>';
      html += '<div id="textinfocsv" style="display:none;">';
      html += ['Word Count', 'Unparsed', 'L1', 'L2', 'L3', 'L4'].join(",") + "<br>";
      html += [wl, counts[0], counts[1], counts[2], counts[3], counts[4]].join(",") + "\n";
      html += '</div>'; 
      $('#textinfo').html(html);
    },
    copyToClipboard: function() {
      var copyText = document.querySelector("#textinfocsv");
      copyText.style.display = "";
      var range = document.createRange();
      range.selectNode(copyText)
      window.getSelection().removeAllRanges();
      window.getSelection().addRange(range);
      document.execCommand("copy");
      window.getSelection().removeAllRanges();
      copyText.style.display = "none";
    }
  };

  /**
   * Input Text Controller
   * 
   * Responsible for managing the input text and showing error messages.
   */
  var inputTextCtrl = {
    getInputText: function() {
      var text = $('#textinput').val().replace(/\s+$/g, '');
      return text;
    },
    error: function(error) {
      var html = '<h4 class="alert-heading">Parse Text Error</h4>';
      html += 'There was a problem parsing the text.<br>';
      if(error.reason) {
        html += '<b>Reason:</b> '+utils.htmlEntities(error.reason)+'<br>';
      }
      if(error.traceback) {
        html += '<hr><pre>' + utils.htmlEntities(error.traceback)+'</pre>';
      }
      $("#parser-error").html(html).removeClass('d-none');
      return this;
    },
    clearError: function() {
      $("#parser-error").addClass('d-none').html('');
      return this;
    },
    clearInput: function() {
      $('#textinput').val('');
      return this;
    },
    showLoadingIndicator: function() {
      $("#parsespinner").removeClass("d-none");
    },
    hideLoadingIndicator: function() {
      $("#parsespinner").addClass("d-none");
    },
    reset: function() {
      this.clearError();
      this.clearInput();
      this.hideLoadingIndicator();
    }
  };

  /**
   * Main Controller
   * 
   * Responsible for handling page-level actions/events and delegating to controllers 
   * for further processing and rendering as appropriate.
   */
  var mainCtrl = {
    api: new ApiClient(),
    onClickParse: function(e) {
      var text = inputTextCtrl.getInputText();
      console.log("parse text: ", text);

      mainCtrl.clearAnalysis();
      inputTextCtrl.clearError();
      inputTextCtrl.showLoadingIndicator();      

      parseService.parse(text).then(function() {
        parsedTextCtrl.render(parseService.data);
        textInfoCtrl.render(parseService.data);
        inputTextCtrl.hideLoadingIndicator();
        utils.scrollTo("#analysis");
      }, function(jqXhr, textStatus) {
        inputTextCtrl.hideLoadingIndicator();
        inputTextCtrl.error(parseService.error);
      });
    },
    onClickClear: function(e) {
      mainCtrl.clearAnalysis();
      inputTextCtrl.reset();
    },
    onClickWord: function(e) {
      var $el = $(e.target);
      if($el.hasClass("highlight")) {
        $el.removeClass("highlight");
        wordInfoCtrl.reset();
      } else {
        $(".word.highlight").removeClass("highlight");
        $el.addClass("highlight");
        var form_ids = parsedTextCtrl.getElementDataFormIds($el);
        var word_info = parseService.getWordInfo(form_ids)
        wordInfoCtrl.setPosition({top: $el.position().top });
        wordInfoCtrl.render(word_info);
      }
      return false;
    },
    onClickUnderlineToggle: function(e) {
      parsedTextCtrl.toggleMultiple();
    },
    onClickLemmaToggle: function(e) {
      parsedTextCtrl.toggleLemmas();
    },
    onClickCopyTextInfo: function(e) {
      textInfoCtrl.copyToClipboard();
    },
    clearAnalysis: function() {
      parsedTextCtrl.reset();
      textInfoCtrl.reset();
      wordInfoCtrl.reset();
      $("#analysis").addClass("d-none");
      return this;
    }
  };

  
  // Page-level event handlers registered here
  $(document).ready(function() {
    $(document).on('click', '#parsebtn', utils.logEvent(mainCtrl.onClickParse));
    $(document).on('click', '#clearbtn', utils.logEvent(mainCtrl.onClickClear));
    $(document).on('click', '.underline-toggle', utils.logEvent(mainCtrl.onClickUnderlineToggle));
    $(document).on('click', '.word.parsed', utils.logEvent(mainCtrl.onClickWord));  
    $(document).on('click', '.lemma-toggle', utils.logEvent(mainCtrl.onClickLemmaToggle));
    $(document).on('click', '#textinfocopy', utils.logEvent(mainCtrl.onClickCopyTextInfo));
    if(window.location.hash == "#demo") {
      window.demo();
    }
  });

    // To run a demo, type demo() in your javascript console....
    window.demo = function() {
      document.querySelector("#textinput").value = `ПРЕСТУПЛЕНИЕ И НАКАЗАНИЕ
РОМАН В ШЕСТИ ЧАСТЯХ С ЭПИЛОГОМ
ЧАСТЬ ПЕРВАЯ

    В начале июля, в чрезвычайно жаркое время, под вечер, один молодой человек вышел из своей каморки, которую нанимал от жильцов в С — м переулке, на улицу и медленно, как бы в нерешимости, отправился к К — ну мосту.

    Он благополучно избегнул встречи с своею хозяйкой на лестнице. Каморка его приходилась под самою кровлей высокого пятиэтажного дома и походила более на шкаф, чем на квартиру. Квартирная же хозяйка его, у которой он нанимал эту каморку с обедом и прислугой, помещалась одною лестницей ниже, в отдельной квартире, и каждый раз, при выходе на улицу, ему непременно надо было проходить мимо хозяйкиной кухни, почти всегда настежь отворенной на лестницу. И каждый раз молодой человек, проходя мимо, чувствовал какое-то болезненное и трусливое ощущение, которого стыдился и от которого морщился. Он был должен кругом хозяйке и боялся с нею встретиться.

    Не то чтоб он был так труслив и забит, совсем даже напротив; но с некоторого времени он был в раздражительном и напряженном состоянии, похожем на ипохондрию. Он до того углубился в себя и уединился от всех, что боялся даже всякой встречи, не только встречи с хозяйкой. Он был задавлен бедностью; но даже стесненное положение перестало в последнее время тяготить его. Насущными делами своими он совсем перестал и не хотел заниматься. Никакой хозяйки, в сущности, он не боялся, что бы та ни замышляла против него. Но останавливаться на лестнице, слушать всякий вздор про всю эту обыденную дребедень, до которой ему нет никакого дела, все эти приставания о платеже, угрозы, жалобы, и при этом самому изворачиваться, извиняться, лгать, — нет уж, лучше проскользнуть как-нибудь кошкой по лестнице и улизнуть, чтобы никто не видал.
`;
    };

})(jQuery);
