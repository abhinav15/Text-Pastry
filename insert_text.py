import sublime, sublime_plugin, re

class OverlayInsertTextCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.items = [
            [ "Sequence: From 1 to X", "Command: \\i" ],
            [ "Sequence: From 0 to X", "Command: \\i0" ],
            [ "Sequence: From N to X by M", "Command: \i(N,M)", ],
            [ "Clipboard: Use Data from Clipboard", "Command: \\p", ],
            [ "Sample Text", "Command: first second third" ],
            [ "Insert Nums Format", "Command: N M P" ]
        ]
        short_descriptions = [
            [ "Inserts a series of numbers, starting at 1." ],
            [ "Inserts a series of numbers, starting at 0." ],
            [ "N: The start number; M: The step size. N and M may be < 0.", "P: Leading zero. Must be > 0" ],
            [ "Uses your clipboard data as insertion list by splitting the words.", "See string.split() for further information." ],
            [ "Words separated by one space."  ],
            [ "Inserts a series of numbers by using the Insert Nums format, starting at N." ]
        ]

        for idx, val in enumerate(self.items):
            for s in short_descriptions[idx]:
                self.items[idx].append(s)
        self.window.show_quick_panel(self.items, self.on_done)

    def on_done(self, index):
        s = ""

        if index >= 0 and index < len(self.items):
            item = self.items[index]
            s = item[1].replace("Command: ", "")
            if s == "\\p":
                self.window.active_view().run_command("insert_text", {"text": sublime.get_clipboard()})
            elif s == "\\i":
                self.window.active_view().run_command("insert_nums", {"current": "1", "step": "1", "padding": "1"})
            elif s == "\\i0":
                self.window.active_view().run_command("insert_nums", {"current": "0", "step": "1", "padding": "1"})

            if len(s):
                self.window.run_command("prompt_insert_text", { "text": s })
                #self.window.show_input_panel('Enter a list of items, separated by spaces', s, None, None, None)

class PromptInsertTextCommand(sublime_plugin.WindowCommand):

    def run(self, text):
        v = self.window.show_input_panel('Enter a list of items, separated by spaces', text, self.on_done, None, None)

    def on_done(self, text):
        try:
            #sublime.status_message("Text: " + str(text))
            if self.window.active_view() and len(text) > 0:
                m1 = re.compile('(-?\d+) (-?\d+) (-?\d+)').match(text)
                m2 = re.compile('\\\\i(\d*)(,(-?\d+))?').match(text)
                m3 = re.compile('\\\\i\((\d*)(,(-?\d+))?\)').match(text)

                if m1:
                    sublime.status_message("Inserting Nums: " + text)
                    (current, step, padding) = map(str, text.split(" "))
                    self.window.active_view().run_command("insert_nums", {"current" : current, "step" : step, "padding" : padding})

                elif m2 or m3:
                    m = None
                    if m2: m = m2
                    else: m = m3
                    current = m.group(1)
                    step = m.group(3)

                    if current is None or len(current) == 0: current = "1"
                    if step is None or len(step) == 0: step = "1"

                    sublime.status_message("Inserting #" + text)
                    self.window.active_view().run_command("insert_nums", {"current" : current, "step" : step, "padding" : "1"})
                elif text == "\\p":
                    sublime.status_message("Inserting from clipboard")
                    self.window.active_view().run_command("insert_text", {"text": sublime.get_clipboard()})
                else:
                    sublime.status_message("Inserting " + text)
                    self.window.active_view().run_command("insert_text", {"text": text})

        except ValueError:
            pass

class InsertTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, text):
        regions = []
        sel = self.view.sel()
        items = text.split()

        for idx, region in enumerate(sel):
            if idx < len(items):
                current = items[idx]
                #sublime.status_message("Inserting #" + current)
                self.view.replace(edit, region, current)
            else:
                regions.append(region)

        sel.clear()

        for region in regions:
            sel.add(sublime.Region(region.begin(), region.end()))
