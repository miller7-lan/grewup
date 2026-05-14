package com.dazzle.secretary;

import android.app.Activity;
import android.os.Bundle;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.*;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class MainActivity extends Activity {
    private static final String PREFS = "dazzle_secretary_mobile";
    private static final String KEY_CLASS = "class_roster";
    private static final String KEY_GRADE = "grade_roster";
    private static final int RED = Color.rgb(255, 75, 75);
    private static final int RED_DARK = Color.rgb(219, 48, 67);
    private static final int RED_SOFT = Color.rgb(255, 239, 241);
    private static final int BG = Color.rgb(250, 247, 249);
    private static final int SURFACE = Color.rgb(255, 255, 255);
    private static final int LINE = Color.rgb(235, 225, 230);
    private static final int TEXT = Color.rgb(34, 38, 52);
    private static final int MUTED = Color.rgb(112, 118, 132);

    private SharedPreferences prefs;
    private RosterBook classBook;
    private RosterBook gradeBook;
    private String role = "班团支书";
    private String gradeScope = "全年级";
    private String editGroup = "";
    private String tab = "核查";
    private CheckResult lastResult;
    private String lastMode = "全班核查";
    private String inputText = "";
    private LinearLayout root;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        classBook = RosterBook.fromJson(loadPrefOrAsset(KEY_CLASS, "class_roster.json"));
        gradeBook = RosterBook.fromJson(loadPrefOrAsset(KEY_GRADE, "grade_roster.json"));
        editGroup = gradeBook.activeClass;
        render();
    }

    private void render() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(BG);
        setContentView(root);

        ScrollView scroll = new ScrollView(this);
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        content.setPadding(dp(16), dp(18), dp(16), dp(14));
        scroll.addView(content);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));

        addHeader(content);
        if ("核查".equals(tab)) renderCheck(content);
        else if ("底册".equals(tab)) renderRoster(content);
        else if ("结果".equals(tab)) renderResult(content);
        else renderHistory(content);
        addBottomNav();
    }

    private void addHeader(LinearLayout parent) {
        LinearLayout hero = new LinearLayout(this);
        hero.setOrientation(LinearLayout.VERTICAL);
        hero.setGravity(Gravity.CENTER_HORIZONTAL);
        hero.setPadding(dp(16), dp(14), dp(16), dp(12));
        hero.setBackground(rounded(SURFACE, 22, dp(1), LINE));
        hero.setElevation(dp(2));
        LinearLayout.LayoutParams heroLp = new LinearLayout.LayoutParams(-1, -2);
        heroLp.setMargins(0, 0, 0, dp(12));
        parent.addView(hero, heroLp);

        TextView title = text("Dazzle Secretary", 25, true, TEXT);
        title.setGravity(Gravity.CENTER);
        hero.addView(title);
        TextView subtitle = text("本地名单核查 · Android 首版", 13, false, MUTED);
        subtitle.setPadding(0, dp(2), 0, 0);
        subtitle.setGravity(Gravity.CENTER);
        hero.addView(subtitle);

        RadioGroup roleGroup = new RadioGroup(this);
        roleGroup.setOrientation(RadioGroup.HORIZONTAL);
        roleGroup.setGravity(Gravity.CENTER);
        roleGroup.setPadding(0, dp(12), 0, dp(4));
        addRadio(roleGroup, "班团支书", role);
        addRadio(roleGroup, "年团支书", role);
        roleGroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            public void onCheckedChanged(RadioGroup group, int checkedId) {
                RadioButton rb = findViewById(checkedId);
                role = rb.getText().toString();
                lastResult = null;
                if ("年团支书".equals(role) && !gradeBook.classes.containsKey(editGroup)) {
                    editGroup = gradeBook.activeClass;
                }
                render();
            }
        });
        parent.addView(roleGroup);

        if ("年团支书".equals(role)) addScopeChooser(parent);
        addStats(parent);
    }

    private void addScopeChooser(LinearLayout parent) {
        TextView label = text("年级核查范围", 13, true, MUTED);
        label.setGravity(Gravity.CENTER);
        parent.addView(label);
        Spinner spinner = new Spinner(this);
        ArrayList<String> options = new ArrayList<>();
        options.add("全年级");
        options.addAll(gradeBook.classNames());
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, options);
        spinner.setAdapter(adapter);
        spinner.setSelection(Math.max(0, options.indexOf(gradeScope)));
        spinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
                String selected = options.get(position);
                if (!selected.equals(gradeScope)) {
                    gradeScope = selected;
                    lastResult = null;
                    render();
                }
            }
            public void onNothingSelected(android.widget.AdapterView<?> parent) {}
        });
        parent.addView(spinner);
    }

    private void addStats(LinearLayout parent) {
        Roster scopeRoster = currentRoster();
        Roster displayRoster = "年团支书".equals(role) ? gradeBook.mergeAll() : scopeRoster;
        int[] display = displayRoster.counts();
        LinearLayout grid = new LinearLayout(this);
        grid.setOrientation(LinearLayout.VERTICAL);
        grid.addView(rowCards(new String[]{"党员", "团员"}, new int[]{display[0], display[1]}));
        grid.addView(rowCards(new String[]{"群众", "总计"}, new int[]{display[2], display[3]}));
        parent.addView(grid);

        if ("年团支书".equals(role) && !"全年级".equals(gradeScope)) {
            int[] scoped = scopeRoster.counts();
            TextView detail = text("当前分组：" + gradeScope + " · " + scoped[3] + " 人 · 党员 " + scoped[0] + " / 团员 " + scoped[1] + " / 群众 " + scoped[2], 13, false, MUTED);
            detail.setPadding(0, dp(4), 0, dp(8));
            detail.setGravity(Gravity.CENTER);
            parent.addView(detail);
        }
    }

    private LinearLayout rowCards(String[] labels, int[] values) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(0, dp(8), 0, 0);
        for (int i = 0; i < labels.length; i++) {
            LinearLayout card = card();
            card.setGravity(Gravity.CENTER);
            TextView label = text(labels[i], 13, false, MUTED);
            label.setGravity(Gravity.CENTER);
            card.addView(label);
            TextView value = text(String.valueOf(values[i]), 28, true, RED);
            value.setGravity(Gravity.CENTER);
            card.addView(value);
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, -2, 1);
            lp.setMargins(i == 0 ? 0 : dp(6), 0, i == 0 ? dp(6) : 0, 0);
            row.addView(card, lp);
        }
        return row;
    }

    private void renderCheck(LinearLayout parent) {
        final String[] modes = {"全班核查", "仅核查团员", "仅核查党员"};
        parent.addView(sectionTitle("立即核查"));
        Spinner modeSpinner = new Spinner(this);
        modeSpinner.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, modes));
        modeSpinner.setSelection(indexOf(modes, lastMode));
        modeSpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) { lastMode = modes[pos]; }
            public void onNothingSelected(android.widget.AdapterView<?> p) {}
        });
        parent.addView(modeSpinner);

        final EditText input = new EditText(this);
        input.setMinLines(8);
        input.setGravity(Gravity.TOP);
        input.setText(inputText);
        input.setHint("粘贴微信接龙、完成名单或任意包含姓名的文本");
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        input.setBackground(rounded(SURFACE, 18, dp(1), LINE));
        input.setPadding(dp(14), dp(14), dp(14), dp(14));
        LinearLayout.LayoutParams inputLp = new LinearLayout.LayoutParams(-1, -2);
        inputLp.setMargins(0, dp(10), 0, dp(12));
        parent.addView(input, inputLp);

        Button check = primaryButton("开始核查");
        check.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                inputText = input.getText().toString();
                hideKeyboard(input);
                if (currentRoster().total() == 0) {
                    toast("请先到底册页录入名单");
                    return;
                }
                if (inputText.trim().isEmpty()) {
                    toast("请先粘贴完成情况文本");
                    return;
                }
                lastResult = checkText(inputText, currentRoster().targets(lastMode), lastMode);
                saveHistory(lastResult);
                tab = "结果";
                render();
            }
        });
        parent.addView(check);

        if (lastResult != null) addResultSummary(parent, lastResult);
    }

    private void renderRoster(LinearLayout parent) {
        parent.addView(sectionTitle("底册管理"));
        if ("年团支书".equals(role)) {
            addGradeRosterTools(parent);
        }
        final Roster editRoster = "年团支书".equals(role) ? gradeBook.get(editGroup) : classBook.get(classBook.activeClass);
        TextView current = text(("年团支书".equals(role) ? "当前维护分组：" + editGroup : "正在维护：本班"), 14, true, TEXT);
        current.setGravity(Gravity.CENTER);
        parent.addView(current);
        final EditText party = rosterBox("党员名单", editRoster.groupParty);
        final EditText member = rosterBox("团员名单", editRoster.groupA);
        final EditText other = rosterBox("群众名单", editRoster.groupB);
        addRosterCategory(parent, "党员", party);
        addRosterCategory(parent, "团员", member);
        addRosterCategory(parent, "群众", other);
        Button save = primaryButton("保存底册");
        save.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                Roster cleaned = Roster.clean(lines(party), lines(member), lines(other));
                if ("年团支书".equals(role)) {
                    gradeBook.put(editGroup, cleaned);
                    gradeBook.activeClass = editGroup;
                    saveBook(KEY_GRADE, gradeBook);
                } else {
                    classBook.put(classBook.activeClass, cleaned);
                    saveBook(KEY_CLASS, classBook);
                }
                toast("底册已保存");
                render();
            }
        });
        parent.addView(save);
    }

    private void addRosterCategory(LinearLayout parent, String label, final EditText editText) {
        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.HORIZONTAL);
        header.setGravity(Gravity.CENTER_VERTICAL);
        TextView title = text(label, 17, true, TEXT);
        header.addView(title, new LinearLayout.LayoutParams(0, -2, 1));
        Button copy = smallButton("复制");
        copy.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                cm.setPrimaryClip(ClipData.newPlainText("names", editText.getText().toString()));
                toast("名单已复制");
            }
        });
        header.addView(copy);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.setMargins(0, dp(14), 0, 0);
        parent.addView(header, lp);
        parent.addView(editText);
    }

    private void addGradeRosterTools(LinearLayout parent) {
        Spinner groupSpinner = new Spinner(this);
        ArrayList<String> names = gradeBook.classNames();
        groupSpinner.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, names));
        groupSpinner.setSelection(Math.max(0, names.indexOf(editGroup)));
        groupSpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                String selected = names.get(pos);
                if (!selected.equals(editGroup)) {
                    editGroup = selected;
                    render();
                }
            }
            public void onNothingSelected(android.widget.AdapterView<?> p) {}
        });
        parent.addView(groupSpinner);

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        final EditText newName = new EditText(this);
        newName.setHint("新增分组名");
        row.addView(newName, new LinearLayout.LayoutParams(0, -2, 1));
        Button add = smallButton("添加");
        add.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                String name = newName.getText().toString().trim();
                if (name.isEmpty()) {
                    toast("请输入分组名");
                    return;
                }
                gradeBook.put(name, new Roster());
                gradeBook.activeClass = name;
                editGroup = name;
                saveBook(KEY_GRADE, gradeBook);
                render();
            }
        });
        row.addView(add);
        Button del = smallButton("删除");
        del.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (gradeBook.classes.size() <= 1) {
                    toast("至少保留一个分组");
                    return;
                }
                gradeBook.classes.remove(editGroup);
                editGroup = gradeBook.classNames().get(0);
                gradeBook.activeClass = editGroup;
                if (gradeScope.equals(editGroup)) gradeScope = "全年级";
                saveBook(KEY_GRADE, gradeBook);
                render();
            }
        });
        row.addView(del);
        parent.addView(row);
    }

    private void renderResult(LinearLayout parent) {
        parent.addView(sectionTitle("核查结果"));
        if (lastResult == null) {
            parent.addView(text("还没有核查结果。先到「核查」页粘贴文本并开始核查。", 15, false, MUTED));
            return;
        }
        addResultSummary(parent, lastResult);
        if ("年团支书".equals(role)) addGradeSummary(parent, lastResult);
        parent.addView(sectionTitle("未完成名单"));
        parent.addView(tagBlock(lastResult.missing, "#FFF1F2", "#BE123C"));
        Button copy = primaryButton("复制提醒话术");
        copy.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                ClipboardManager cm = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                cm.setPrimaryClip(ClipData.newPlainText("reminder", lastResult.reminder()));
                toast("已复制");
            }
        });
        parent.addView(copy);
        parent.addView(sectionTitle("已完成名单"));
        parent.addView(tagBlock(lastResult.done, "#ECFDF3", "#027A48"));
        if (!lastResult.unknown.isEmpty()) {
            parent.addView(sectionTitle("未在底册中"));
            parent.addView(tagBlock(lastResult.unknown, "#FFFAEB", "#B54708"));
        }
    }

    private void addResultSummary(LinearLayout parent, CheckResult result) {
        LinearLayout card = card();
        card.setGravity(Gravity.CENTER);
        TextView title = text(result.mode + " · " + result.percentText(), 18, true, TEXT);
        title.setGravity(Gravity.CENTER);
        card.addView(title);
        TextView summary = text("应核查 " + result.total + " 人，已完成 " + result.done.size() + " 人，未完成 " + result.missing.size() + " 人", 14, false, MUTED);
        summary.setGravity(Gravity.CENTER);
        card.addView(summary);
        parent.addView(card);
    }

    private void addGradeSummary(LinearLayout parent, CheckResult result) {
        parent.addView(sectionTitle("年级汇总对比"));
        Set<String> done = new HashSet<>(result.done);
        for (String name : gradeBook.classNames()) {
            List<String> targets = gradeBook.get(name).targets(result.mode);
            int complete = 0;
            for (String target : targets) if (done.contains(target)) complete++;
            int total = targets.size();
            LinearLayout card = card();
            card.setGravity(Gravity.CENTER);
            TextView groupName = text(name, 16, true, TEXT);
            groupName.setGravity(Gravity.CENTER);
            card.addView(groupName);
            TextView line = text("应核查 " + total + " · 已完成 " + complete + " · 未完成 " + (total - complete) + " · 完成率 " + pct(complete, total), 13, false, MUTED);
            line.setGravity(Gravity.CENTER);
            card.addView(line);
            parent.addView(card);
        }
    }

    private void renderHistory(LinearLayout parent) {
        parent.addView(sectionTitle("最近记录"));
        String raw = prefs.getString("history", "[]");
        try {
            JSONArray arr = new JSONArray(raw);
            if (arr.length() == 0) {
                TextView empty = text("暂无记录。", 15, false, MUTED);
                empty.setGravity(Gravity.CENTER);
                parent.addView(empty);
            }
            for (int i = arr.length() - 1; i >= 0; i--) {
                JSONObject item = arr.getJSONObject(i);
                LinearLayout card = card();
                card.setGravity(Gravity.CENTER);
                TextView title = text(item.optString("title"), 16, true, TEXT);
                title.setGravity(Gravity.CENTER);
                card.addView(title);
                TextView summary = text(item.optString("summary"), 13, false, MUTED);
                summary.setGravity(Gravity.CENTER);
                card.addView(summary);
                parent.addView(card);
            }
        } catch (Exception e) {
            parent.addView(text("记录读取失败。", 15, false, MUTED));
        }
        Button clear = smallButton("清空记录");
        clear.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                prefs.edit().putString("history", "[]").apply();
                render();
            }
        });
        parent.addView(clear);
    }

    private CheckResult checkText(String raw, List<String> targets, String mode) {
        String clean = raw.replaceAll("[^\\u4e00-\\u9fa5a-zA-Z0-9]", "");
        LinkedHashSet<String> done = new LinkedHashSet<>();
        for (String name : targets) {
            if (raw.contains(name) || clean.contains(name)) done.add(name);
        }
        LinkedHashSet<String> unknown = new LinkedHashSet<>();
        LinkedHashSet<String> targetSet = new LinkedHashSet<>(targets);
        String chinese = raw.replaceAll("[^\\u4e00-\\u9fa5\\n\\r\\t ,，、;；]", " ");
        for (String token : chinese.split("[\\s,，、;；]+")) {
            String n = normalizeName(token);
            if (n.length() >= 2 && !targetSet.contains(n)) unknown.add(n);
        }
        ArrayList<String> missing = new ArrayList<>();
        for (String name : targets) if (!done.contains(name)) missing.add(name);
        return new CheckResult(mode, targets.size(), new ArrayList<>(done), missing, new ArrayList<>(unknown));
    }

    private Roster currentRoster() {
        if (!"年团支书".equals(role)) return classBook.get(classBook.activeClass);
        if ("全年级".equals(gradeScope)) return gradeBook.mergeAll();
        return gradeBook.get(gradeScope);
    }

    private void saveHistory(CheckResult result) {
        try {
            JSONArray arr = new JSONArray(prefs.getString("history", "[]"));
            JSONObject item = new JSONObject();
            item.put("title", scopeLabel() + " · " + result.mode);
            item.put("summary", "完成率 " + result.percentText() + " · 未完成 " + result.missing.size() + " 人");
            arr.put(item);
            while (arr.length() > 20) arr.remove(0);
            prefs.edit().putString("history", arr.toString()).apply();
        } catch (Exception ignored) {}
    }

    private String scopeLabel() {
        return "年团支书".equals(role) ? gradeScope : "本班";
    }

    private EditText rosterBox(String label, List<String> names) {
        EditText edit = new EditText(this);
        edit.setHint(label + "（每行一个名字）");
        edit.setText(join(names, "\n"));
        edit.setMinLines(5);
        edit.setGravity(Gravity.TOP);
        edit.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        edit.setBackground(rounded(SURFACE, 18, dp(1), LINE));
        edit.setPadding(dp(14), dp(14), dp(14), dp(14));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.setMargins(0, dp(10), 0, 0);
        edit.setLayoutParams(lp);
        return edit;
    }

    private LinearLayout tagBlock(List<String> names, String bg, String fg) {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        if (names.isEmpty()) {
            box.addView(text("无", 14, false, MUTED));
            return box;
        }
        TextView tv = text(join(names, "  "), 15, false, Color.parseColor(fg));
        tv.setBackground(rounded(Color.parseColor(bg), 16, 0, Color.TRANSPARENT));
        tv.setPadding(dp(12), dp(10), dp(12), dp(10));
        box.addView(tv);
        return box;
    }

    private void addBottomNav() {
        LinearLayout nav = new LinearLayout(this);
        nav.setOrientation(LinearLayout.HORIZONTAL);
        nav.setBackgroundColor(SURFACE);
        nav.setPadding(dp(10), dp(8), dp(10), dp(10));
        nav.setElevation(dp(8));
        String[] tabs = {"核查", "底册", "结果", "记录"};
        for (final String item : tabs) {
            Button b = new Button(this);
            b.setText(item);
            boolean selected = item.equals(tab);
            b.setTextColor(selected ? RED_DARK : MUTED);
            b.setAllCaps(false);
            b.setTextSize(14);
            b.setBackground(rounded(selected ? RED_SOFT : Color.TRANSPARENT, 18, 0, Color.TRANSPARENT));
            b.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    tab = item;
                    render();
                }
            });
            LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(48), 1);
            lp.setMargins(dp(3), 0, dp(3), 0);
            nav.addView(b, lp);
        }
        root.addView(nav);
    }

    private TextView sectionTitle(String value) {
        TextView tv = text(value, 18, true, TEXT);
        tv.setGravity(Gravity.CENTER);
        tv.setPadding(0, dp(18), 0, dp(8));
        return tv;
    }

    private LinearLayout card() {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setBackground(rounded(SURFACE, 20, dp(1), LINE));
        card.setElevation(dp(2));
        card.setPadding(dp(16), dp(14), dp(16), dp(14));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.setMargins(0, dp(9), 0, dp(5));
        card.setLayoutParams(lp);
        return card;
    }

    private Button primaryButton(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextColor(Color.WHITE);
        b.setTextSize(17);
        b.setAllCaps(false);
        b.setBackground(rounded(RED, 22, 0, Color.TRANSPARENT));
        b.setMinHeight(dp(52));
        b.setElevation(dp(2));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.setMargins(0, dp(4), 0, dp(4));
        b.setLayoutParams(lp);
        return b;
    }

    private Button smallButton(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setAllCaps(false);
        b.setTextColor(RED_DARK);
        b.setBackground(rounded(RED_SOFT, 16, dp(1), Color.rgb(255, 214, 220)));
        return b;
    }

    private TextView text(String value, int sp, boolean bold, int color) {
        TextView tv = new TextView(this);
        tv.setText(value);
        tv.setTextSize(sp);
        tv.setTextColor(color);
        tv.setIncludeFontPadding(true);
        if (bold) tv.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return tv;
    }

    private void addRadio(RadioGroup group, String value, String selected) {
        RadioButton rb = new RadioButton(this);
        rb.setText(value);
        rb.setTextSize(15);
        rb.setTextColor(TEXT);
        rb.setId(View.generateViewId());
        rb.setChecked(value.equals(selected));
        group.addView(rb);
    }

    private GradientDrawable rounded(int color, int radiusDp, int strokeWidth, int strokeColor) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(dp(radiusDp));
        if (strokeWidth > 0) drawable.setStroke(strokeWidth, strokeColor);
        return drawable;
    }

    private String loadPrefOrAsset(String key, String assetName) {
        String value = prefs.getString(key, null);
        if (value != null) return value;
        try {
            BufferedReader br = new BufferedReader(new InputStreamReader(getAssets().open(assetName), "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) sb.append(line);
            br.close();
            value = sb.toString();
            prefs.edit().putString(key, value).apply();
            return value;
        } catch (Exception e) {
            return "{\"active_class\":\"默认\",\"classes\":{\"默认\":{\"group_party\":[],\"group_a\":[],\"group_b\":[]}}}";
        }
    }

    private void saveBook(String key, RosterBook book) {
        prefs.edit().putString(key, book.toJson().toString()).apply();
    }

    private ArrayList<String> lines(EditText edit) {
        ArrayList<String> result = new ArrayList<>();
        for (String line : edit.getText().toString().split("\\n")) {
            String name = normalizeName(line);
            if (name.length() >= 2 && !result.contains(name)) result.add(name);
        }
        return result;
    }

    private static String normalizeName(String value) {
        return value == null ? "" : value.replaceAll("[^\\u4e00-\\u9fa5]", "").trim();
    }

    private String join(List<String> values, String sep) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) sb.append(sep);
            sb.append(values.get(i));
        }
        return sb.toString();
    }

    private String pct(int done, int total) {
        if (total == 0) return "0.0%";
        return String.format(java.util.Locale.CHINA, "%.1f%%", done * 100.0 / total);
    }

    private int indexOf(String[] arr, String value) {
        for (int i = 0; i < arr.length; i++) if (arr[i].equals(value)) return i;
        return 0;
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private void toast(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }

    private void hideKeyboard(View view) {
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        if (imm != null) imm.hideSoftInputFromWindow(view.getWindowToken(), 0);
    }

    static class Roster {
        ArrayList<String> groupParty = new ArrayList<>();
        ArrayList<String> groupA = new ArrayList<>();
        ArrayList<String> groupB = new ArrayList<>();

        static Roster clean(List<String> party, List<String> members, List<String> others) {
            Roster r = new Roster();
            r.groupParty = unique(party, null, null);
            r.groupA = unique(members, new HashSet<>(r.groupParty), null);
            HashSet<String> blocked = new HashSet<>(r.groupParty);
            blocked.addAll(r.groupA);
            r.groupB = unique(others, blocked, null);
            return r;
        }

        static Roster fromJson(JSONObject obj) {
            Roster r = new Roster();
            r.groupParty = jsonArray(obj.optJSONArray("group_party"));
            r.groupA = jsonArray(obj.optJSONArray("group_a"));
            r.groupB = jsonArray(obj.optJSONArray("group_b"));
            return clean(r.groupParty, r.groupA, r.groupB);
        }

        JSONObject toJson() {
            JSONObject obj = new JSONObject();
            try {
                obj.put("group_party", new JSONArray(groupParty));
                obj.put("group_a", new JSONArray(groupA));
                obj.put("group_b", new JSONArray(groupB));
            } catch (Exception ignored) {}
            return obj;
        }

        List<String> targets(String mode) {
            ArrayList<String> result = new ArrayList<>();
            if ("仅核查党员".equals(mode)) result.addAll(groupParty);
            else if ("仅核查团员".equals(mode)) result.addAll(groupA);
            else {
                result.addAll(groupParty);
                result.addAll(groupA);
                result.addAll(groupB);
            }
            return result;
        }

        int total() { return groupParty.size() + groupA.size() + groupB.size(); }
        int[] counts() { return new int[]{groupParty.size(), groupA.size(), groupB.size(), total()}; }
    }

    static class RosterBook {
        String activeClass = "默认";
        LinkedHashMap<String, Roster> classes = new LinkedHashMap<>();

        static RosterBook fromJson(String raw) {
            RosterBook book = new RosterBook();
            try {
                JSONObject root = new JSONObject(raw);
                book.activeClass = root.optString("active_class", "默认");
                JSONObject classesObj = root.optJSONObject("classes");
                if (classesObj != null) {
                    JSONArray names = classesObj.names();
                    if (names != null) {
                        ArrayList<String> ordered = new ArrayList<>();
                        for (int i = 0; i < names.length(); i++) ordered.add(names.getString(i));
                        Collections.sort(ordered);
                        for (String name : ordered) book.classes.put(name, Roster.fromJson(classesObj.getJSONObject(name)));
                    }
                }
            } catch (Exception ignored) {}
            if (book.classes.isEmpty()) book.classes.put("默认", new Roster());
            if (!book.classes.containsKey(book.activeClass)) book.activeClass = book.classNames().get(0);
            return book;
        }

        JSONObject toJson() {
            JSONObject root = new JSONObject();
            JSONObject obj = new JSONObject();
            try {
                for (String name : classes.keySet()) obj.put(name, classes.get(name).toJson());
                root.put("active_class", activeClass);
                root.put("classes", obj);
            } catch (Exception ignored) {}
            return root;
        }

        ArrayList<String> classNames() {
            return new ArrayList<>(classes.keySet());
        }

        Roster get(String name) {
            Roster r = classes.get(name);
            if (r == null) {
                r = new Roster();
                classes.put(name, r);
            }
            return r;
        }

        void put(String name, Roster roster) {
            classes.put(name, roster);
        }

        Roster mergeAll() {
            ArrayList<String> p = new ArrayList<>();
            ArrayList<String> a = new ArrayList<>();
            ArrayList<String> b = new ArrayList<>();
            for (Roster r : classes.values()) {
                p.addAll(r.groupParty);
                a.addAll(r.groupA);
                b.addAll(r.groupB);
            }
            return Roster.clean(p, a, b);
        }
    }

    static class CheckResult {
        String mode;
        int total;
        ArrayList<String> done;
        ArrayList<String> missing;
        ArrayList<String> unknown;

        CheckResult(String mode, int total, ArrayList<String> done, ArrayList<String> missing, ArrayList<String> unknown) {
            this.mode = mode;
            this.total = total;
            this.done = done;
            this.missing = missing;
            this.unknown = unknown;
        }

        String percentText() {
            if (total == 0) return "0.0%";
            return String.format(java.util.Locale.CHINA, "%.1f%%", done.size() * 100.0 / total);
        }

        String reminder() {
            if (missing.isEmpty()) return "本次已全部完成。";
            StringBuilder sb = new StringBuilder("未完成提醒：");
            for (String name : missing) sb.append("@").append(name).append(" ");
            return sb.toString().trim();
        }
    }

    private static ArrayList<String> jsonArray(JSONArray arr) {
        ArrayList<String> out = new ArrayList<>();
        if (arr == null) return out;
        for (int i = 0; i < arr.length(); i++) {
            String name = normalizeName(arr.optString(i));
            if (name.length() >= 2 && !out.contains(name)) out.add(name);
        }
        return out;
    }

    private static ArrayList<String> unique(List<String> values, Set<String> blocked, Set<String> unused) {
        LinkedHashSet<String> seen = new LinkedHashSet<>();
        ArrayList<String> out = new ArrayList<>();
        for (String value : values) {
            String name = normalizeName(value);
            if (name.length() >= 2 && (blocked == null || !blocked.contains(name)) && !seen.contains(name)) {
                out.add(name);
                seen.add(name);
            }
        }
        return out;
    }
}
