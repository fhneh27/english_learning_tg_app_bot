import { InputHTMLAttributes, TextareaHTMLAttributes } from "react";

type SharedInputProps = {
  className?: string;
  label?: string;
  multiline?: boolean;
};

type TextInputProps = SharedInputProps & InputHTMLAttributes<HTMLInputElement>;
type TextAreaProps = SharedInputProps & TextareaHTMLAttributes<HTMLTextAreaElement>;

function Input(props: TextInputProps | TextAreaProps) {
  const { className = "", label, multiline = false, ...restProps } = props;
  const wrapperClassName = ["input-field", className].filter(Boolean).join(" ");

  return (
    <label className={wrapperClassName}>
      {label ? <span className="input-label">{label}</span> : null}
      {multiline ? (
        <textarea {...(restProps as TextAreaProps)} className="input-control input-control-textarea" />
      ) : (
        <input {...(restProps as TextInputProps)} className="input-control" />
      )}
    </label>
  );
}

export default Input;
