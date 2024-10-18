export interface IGameData {
  checker_positions: { [fiels: string]: string[] };
  dices: {
    value: number;
    randomized: boolean;
  }[];
}
