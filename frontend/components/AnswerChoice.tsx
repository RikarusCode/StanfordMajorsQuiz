interface AnswerChoiceProps {
  value: number;
  label: string;
  isSelected: boolean;
  onClick: () => void;
}

export default function AnswerChoice({
  value,
  label,
  isSelected,
  onClick,
}: AnswerChoiceProps) {
  return (
    <button
      onClick={onClick}
      className={[
        "w-full p-5 rounded-xl text-left",
        "transition-colors duration-100",
        "relative overflow-hidden",
        "tile",
        isSelected ? "tile-selected" : "",
      ].join(" ")}
    >
      {/* Selected indicator */}
      {isSelected && (
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-blue-600/20 to-transparent" />
      )}
      
      <div className="relative flex items-center justify-between">
        <span
          className={`font-medium text-lg ${
            isSelected ? "text-white" : "text-gray-200"
          }`}
        >
          {label}
        </span>
        <div className="flex items-center gap-3">
          {/* Value badge */}
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${
              isSelected ? "bg-blue-500 text-white" : "bg-white/10 text-gray-400"
            }`}
          >
            {value}
          </span>
          
          {/* Checkmark for selected */}
          {isSelected && (
            <svg
              className="w-6 h-6 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M5 13l4 4L19 7"
              />
            </svg>
          )}
        </div>
      </div>
    </button>
  );
}
