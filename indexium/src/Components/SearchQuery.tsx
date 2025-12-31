import { FormEvent, ChangeEvent } from "react";
import { useSearch } from "./hooks/useSearch";
import { Input } from "@/Components/ui/input";
import { Button } from "@/Components/ui/button";
import { Search } from "lucide-react";

export const SearchBar = () => {
  const { query, setQuery, handleSubmit } = useSearch();

  // Optional: type-safe onChange handler
  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  return (
    <form
      onSubmit={(e: FormEvent<HTMLFormElement>) => handleSubmit(e)}
      className="flex items-center gap-2 w-full max-w-lg mx-auto"
    >
      <div className="relative flex-1">
        <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
        <Input
          type="text"
          value={query}
          onChange={onChange}
          placeholder="Search..."
          className="pl-10"
        />
      </div>
      <Button type="submit" className="bg-blue-500 hover:bg-blue-600">
        Submit
      </Button>
    </form>
  );
};
