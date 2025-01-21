APP_CSS = """
    #button-container {
        height: auto;
        align: left middle;
        padding: 1 0;
    }

    #button-container Button {
        background: $primary;
        color: $text;
        margin: 0 1;
        padding: 0 2;
        height: 3;
        border: $primary;
    }

    #main-content {
        height: 1fr;
    }

    #rich-log {
        width: 60%;
        height: 100%;
        border: solid $panel;
        margin: 1;
        box-sizing: border-box;
        background: $surface;
        color: $text;
    }

    #rich-log:focus {
    border: outer $primary-darken-2;
    }

    #data-table {
        width: 40%;
        height: 100%;
        border: solid $panel;
        margin: 1;
        box-sizing: border-box;
    }

    #data-table:focus {
    border: outer $primary-darken-2;
    }

    Screen {
        overflow: hidden;
    }
"""