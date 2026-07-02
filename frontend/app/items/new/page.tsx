import { AuthGuard } from "@/components/auth-guard";
import { ItemForm } from "@/components/item-form";

export default function NewItemPage() {
  return (
    <AuthGuard>
      <ItemForm mode="create" />
    </AuthGuard>
  );
}
