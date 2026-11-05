import { PositionResponse } from '../competence/position.model';
import { EnterpriseResponse } from './enterprise.model';
import { RoleResponse, UserRoleName } from './role.model';

export interface UserCreate {
  cpf: string;
  name: string;
  email: string;
  password: string;
  np: string;
  role_id: number;
  manager_id?: number | null;
  position_id: number;
  enterprise_id: number;
}

export interface UserResponse {
  id: number;
  cpf: string;
  name: string;
  email: string;
  np: string;
  role: UserRoleName | string;
  manager?: string | null;
  position: string;
  enterprise: string;
}

export interface UserSimpleResponse {
  id: number;
  name: string;
  email: string;
  np: string;
}

export interface UserDetailResponse {
  id: number;
  cpf: string;
  name: string;
  email: string;
  np: string;
  role: RoleResponse;
  position: PositionResponse;
  enterprise: EnterpriseResponse;
  manager?: UserSimpleResponse | null;
}

export interface UserCreateResponse {
  message: string;
  user: UserResponse;
}

export interface UserLogin {
  email?: string | null;
  np?: string | null;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface JwtPayload {
  sub: string;
  user_id: number;
  role: UserRoleName | string;
  enterprise_id: number;
  exp: number;
}
