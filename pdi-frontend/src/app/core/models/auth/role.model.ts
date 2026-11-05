export type UserRoleName = 'Colaborador' | 'Gestor' | 'Recursos Humanos';

export interface RoleResponse {
  id: number;
  name: UserRoleName | string;
}
