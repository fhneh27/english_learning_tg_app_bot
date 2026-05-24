import { FormEvent, useState } from "react";

type EntryFormProps = {
  isSubmitting: boolean;
  onSubmit: (text: string) => Promise<void>;
};

function EntryForm({ isSubmitting, onSubmit }: EntryFormProps) {
  const [text, setText] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedText = text.trim();
    if (!trimmedText) {
      return;
    }

    await onSubmit(trimmedText);
    setText("");
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">New Entry</p>
          <h2>Add a word or phrase</h2>
        </div>
      </div>

      <form className="entry-form" onSubmit={handleSubmit}>
        <textarea
          className="text-area"
          placeholder="For example: shallow, take it easy, or a short sentence"
          rows={4}
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <button className="primary-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : "Analyze and save"}
        </button>
      </form>
    </section>
  );
}

export default EntryForm;
