type Props = {
  message?: string | null;
};

export default function FieldError({ message }: Props) {
  if (!message) return null;
  return <p className="text-xs text-danger mt-1">{message}</p>;
}
