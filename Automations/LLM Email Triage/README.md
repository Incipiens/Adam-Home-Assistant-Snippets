# LLM Email Triage with Home Assistant

This folder contains an automation that uses a language model to triage incoming emails and categorize them based on their content. The automation is written for Home Assistant and can be customized to fit your specific needs.

Note, the actions "ARCHIVE" and "SNOOZE_1H" do not exist in Home Assistant natively. You will need to replace these with actions that make sense for your setup.

This was written for an XDA article, which you can read [here](https://www.xda-developers.com/set-up-email-triage-system-home-assistant-local-llm/).

One can optionally add a to-do list function using the following code, assuming that an "email followups" to-do list exists.

```yaml
  - if:
      - condition: template
        value_template: "{{ triage_obj.actions.create_task is defined }}"
    then:
      - action: todo.add_item
        target:
          entity_id: todo.email_followups
        data:
          item: "{{ triage_obj.actions.create_task.title }}"
          due_datetime: "{{ triage_obj.actions.create_task.due | default(none) }}"
```