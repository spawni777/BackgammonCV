export const base64ToBlob = (base64: string) => {
    const byteString = atob(base64.split(',')[1]);
    const mimeString = base64.split(',')[0].split(':')[1].split(';')[0];
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uint8Array = new Uint8Array(arrayBuffer);

    for (let i = 0; i < byteString.length; i++) {
        uint8Array[i] = byteString.charCodeAt(i);
    }

    return new Blob([uint8Array], { type: mimeString });
};

export const generateStartPosition = () => {
    const checkerPositions: { [key: string]: string[] } = {};

    for (let i = 1; i <= 24; i++) {
        checkerPositions[i.toString()] = [];
    }

    checkerPositions["1"] = ["player_1", "player_1"];
    checkerPositions["12"] = ["player_1", "player_1", "player_1", "player_1", "player_1"];
    checkerPositions["17"] = ["player_1", "player_1", "player_1"];
    checkerPositions["19"] = ["player_1", "player_1", "player_1", "player_1", "player_1"];

    checkerPositions["24"] = ["player_2", "player_2"];
    checkerPositions["13"] = ["player_2", "player_2", "player_2", "player_2", "player_2"];
    checkerPositions["8"] = ["player_2", "player_2", "player_2"];
    checkerPositions["6"] = ["player_2", "player_2", "player_2", "player_2", "player_2"];

    return checkerPositions;
};