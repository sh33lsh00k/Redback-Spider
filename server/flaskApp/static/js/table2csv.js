(function ($) {
    "use strict";
    const optionsDefaults = {
        /* action='download' options */
        filename: "table.csv",

        /* action='output' options */
        appendTo: "body",

        /* general options */
        separator: ",",
        newline: "\n",
        quoteFields: true,
        trimContent: true,
        excludeColumns: "",
        excludeRows: ""
    };

    let options = {};

    function quote(text) {
        return "\"" + text.replace(/"/g, "\"\"") + "\"";
    }

    // taken from http://stackoverflow.com/questions/3665115/create-a-file-in-memory-for-user-to-download-not-through-server
    function download(filename, text) {
        const element = document.createElement("a");
        element.setAttribute("href", "data:text/csv;charset=utf-8,\ufeff" + encodeURIComponent(text));
        element.setAttribute("download", filename);

        element.style.display = "none";
        document.body.appendChild(element);

        element.click();

        document.body.removeChild(element);
    }

    function convert(table, versionOfScanToDownload) {
        let output = "";



        $(".appendAnalytics .tableHeader").each(function (i, col) {
                    const headerRow = $(col);

                    var scanNameArr = headerRow.parent().prev().text().split("||");
                    var scanName = scanNameArr[scanNameArr.length - 1];

                    if (versionOfScanToDownload != "zzzzzzzzz")
                    {
                        var versionOfScan = scanName.split(" - ")[0].split(": ")[1].trim();
                        if (versionOfScan != versionOfScanToDownload) {
                            return;
                        }
                    }


                    output += scanName;
                    output += options.newline;

                    

                    headerRow.children("th").each(function (i, thData) {
                        output += '"' + $(thData).text() + '"';
                        output += options.separator;
                    });
                    output = output.slice(0, -1); // remove last extra comma
                    output += options.newline;


                    $(headerRow.nextAll()).each(function (index, rowsContainsAnalytics) {
                        
                        // fix error
                        if ($(rowsContainsAnalytics).hasClass("tableHeader")) {
                            return false;
                        }

                        $(rowsContainsAnalytics).children("td").each(function (i, analyticsData) {
                            output += '"' + $(analyticsData).text() + '"';
                            output += options.separator;
                        });
                        output = output.slice(0, -1); // remove last extra comma
                        output += options.newline;

                    });


                    output += options.newline;
                    output += options.newline;

            });


        return output;
    }

    $.fn.table2csv = function (action, opt) {
        if (typeof action === "object") {
            opt = action;
            action = "download";
        } else if (action === undefined) {
            action = "download";
        }

        // type checking
        if (typeof action !== "string") {
            throw new Error("\"action\" argument must be a string");
        }
        if (opt !== undefined && typeof opt !== "object") {
            throw new Error("\"options\" argument must be an object");
        }


        options = $.extend({}, optionsDefaults, opt);


        const table = this.filter("table"); // TODO use $.each

        if (table.length <= 0) {
            throw new Error("table2csv must be called on a <table> element");
        }

        if (table.length > 1) {
            throw new Error("converting multiple table elements at once is not supported yet");
        }

        let csv = convert(table, opt.versionOfScanToDownload);

        switch (action) {
        case "download":
            download(options.filename, csv);
            break;
        case "output":
            $(options.appendTo).append($("<pre>").text(csv));
            break;
        case "return":
            return csv;
        default:
            throw new Error("\"action\" argument must be one of the supported action strings");
        }

        return this;
    };

}(jQuery));
