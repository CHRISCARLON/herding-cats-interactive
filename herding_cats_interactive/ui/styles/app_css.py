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

    #button-container Button.connected-button {
        background: $success-darken-2 !important;
        border: $success-darken-2 !important;
        color: $text;
    }

    #button-container Button.connected-button:focus {
        border: $success-darken-2 !important;
    }

    #button-container Button.no-connection-status {
        background: grey;
        border: none;
    }

    #button-container Button.hot-keys {
        background: $secondary;
        color: black;
        border: none;
    }

    #main-content {
        height: 60%;  /* Main content takes 70% */
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

    #rich-log-2 {
        width: 100%;
        height: 25%;
        border: solid $panel;
        margin: 1;
        box-sizing: border-box;
        background: $surface;
        color: $text;
    }

    #rich-log-2:focus {
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
